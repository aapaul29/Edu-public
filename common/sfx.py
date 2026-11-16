"""Procedural sound effects (no samples, no licensing) and the final audio mix.

Scenes log cues with `cue(self, "whoosh")` (see common/style.py), which are saved
to renders/<name>_cues.json. A video's scenes/make_audio.py then turns those cues
into an effects track, optionally adds the AI voiceover, and muxes everything.
"""
import json
import pathlib
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

SR = 48000
RNG = np.random.default_rng(7)


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def _env(n, attack=0.005, release=0.1):
    """Linear attack, exponential release."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-np.maximum(t - attack, 0) / release)


def _band(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def _low(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


# ------------------------------------------------------------------ one-shots
def whoosh(dur=0.45, lo=250, hi=3500):
    """Airy swoosh for things sliding or fading in."""
    n = int(dur * SR)
    x = _band(RNG.standard_normal(n), lo, hi)
    s = np.sin(np.pi * np.linspace(0, 1, n)) ** 2          # swell up and down
    return 0.6 * x * s / (np.abs(x).max() + 1e-9)


def pop(f0=900, f1=420, dur=0.09):
    """Soft UI pop for text appearing."""
    t = _t(dur)
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return 0.35 * np.sin(ph) * _env(len(t), 0.002, 0.03)


def tick(f=2200, dur=0.03):
    t = _t(dur)
    return 0.25 * np.sin(2 * np.pi * f * t) * _env(len(t), 0.0005, 0.006)


def thump(dur=0.25):
    """Low impact for a push or a hit."""
    t = _t(dur)
    f = 120 * (45 / 120) ** (t / dur)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.08)
    click = _low(RNG.standard_normal(len(t)), 1800) * _env(len(t), 0.0005, 0.01)
    return 0.6 * body + 0.15 * click


def chime(notes=(659.25, 987.77), dur=1.4, gap=0.08):
    """Bright two-note 'success' chime."""
    out = np.zeros(int((dur + gap * len(notes)) * SR))
    for i, f in enumerate(notes):
        t = _t(dur)
        tone = sum(a * np.sin(2 * np.pi * f * k * t) for k, a in ((1, 1.0), (2, 0.35), (3, 0.12)))
        seg = 0.22 * tone * _env(len(t), 0.004, 0.45)
        s = int(i * gap * SR)
        out[s:s + len(seg)] += seg
    return out


def wrong(dur=0.5):
    """Gentle descending two-tone for a failure or a 'hmm'."""
    out = np.zeros(int(dur * SR))
    for i, f in enumerate((440, 330)):
        t = _t(dur / 2)
        tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
        seg = 0.18 * tone * _env(len(t), 0.004, 0.12)
        s = int(i * dur / 2 * SR)
        out[s:s + len(seg)] += seg
    return out


def riser(dur=1.0):
    """Short rising sweep to build tension before a reveal."""
    t = _t(dur)
    f = 200 * (1200 / 200) ** (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    noise = _band(RNG.standard_normal(len(t)), 800, 6000)
    s = (t / dur) ** 2
    return 0.12 * (tone + 0.4 * noise / (np.abs(noise).max() + 1e-9)) * s


ONE_SHOTS = {"whoosh": whoosh, "pop": pop, "tick": tick, "thump": thump,
             "chime": chime, "wrong": wrong, "riser": riser}


# ------------------------------------------------------------------ continuous
def rotor_hum(times, thrust, thrust_hover, blades=2, base_rpm=5200):
    """Quadcopter rotor sound that follows thrust. thrust ~ rpm^2, so rpm ~ sqrt(thrust).

    times/thrust: samples of the thrust curve on the VIDEO timeline [s, N].
    Returns (start_time, audio).
    """
    t0, t1 = times[0], times[-1]
    tt = t0 + _t(t1 - t0)
    u = np.interp(tt, times, np.maximum(thrust, 0))
    rpm = base_rpm * np.sqrt(u / thrust_hover + 1e-6)
    f = blades * rpm / 60.0                                 # blade-pass frequency
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = sum(a * np.sin(k * ph) for k, a in ((1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)))
    air = _band(RNG.standard_normal(len(tt)), 400, 4000)
    air /= np.abs(air).max() + 1e-9
    level = 0.25 + 0.75 * np.clip(u / (2 * thrust_hover), 0, 1)
    fade = np.minimum(1, np.minimum((tt - t0) / 0.15, (t1 - tt) / 0.25))
    return t0, 0.5 * (0.6 * tone / 2.0 + 0.4 * air) * level * fade


def motor_whir(times, effort, effort_max):
    """Electric-motor whine whose pitch and level follow |effort| (e.g. cart force)."""
    t0, t1 = times[0], times[-1]
    tt = t0 + _t(t1 - t0)
    e = np.clip(np.abs(np.interp(tt, times, effort)) / effort_max, 0, 1)
    f = 140 + 520 * e
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
    fade = np.minimum(1, np.minimum((tt - t0) / 0.1, (t1 - tt) / 0.2))
    return t0, 0.22 * tone * (0.15 + 0.85 * e) * fade


def spin_swish(times, omega, omega_ref, brightness=None):
    """Airy swish of a tumbling object (a thrown phone, racket, book): two noise pulses per revolution.

    times: samples on the VIDEO timeline [s]; omega: spin rate [rad/s] at those times (sets pulse rate and level);
    omega_ref: spin rate that gives full level; brightness: optional 0..1 per sample that opens up the highs
    (e.g. while the object is flipping or wobbling). Returns (start_time, audio).
    """
    t0, t1 = times[0], times[-1]
    tt = t0 + _t(t1 - t0)
    w = np.abs(np.interp(tt, times, omega))
    b = np.zeros_like(tt) if brightness is None else np.clip(np.interp(tt, times, brightness), 0, 1)
    ph = np.cumsum(2 * w / (2 * np.pi)) / SR                 # pulses (revolutions x 2)
    pulse = (0.5 - 0.5 * np.cos(2 * np.pi * ph)) ** 3
    n = len(tt)
    low = _band(RNG.standard_normal(n), 250, 1800)
    high = _band(RNG.standard_normal(n), 1500, 6000)
    low /= np.abs(low).max() + 1e-9
    high /= np.abs(high).max() + 1e-9
    level = np.clip(w / omega_ref, 0, 1.5)
    fade = np.minimum(1, np.minimum((tt - t0) / 0.15, (t1 - tt) / 0.2))
    return t0, 0.35 * (low + 0.8 * b * high) * (0.25 + 0.75 * pulse) * level * fade



def tone_follow(times, value, vmin, vmax, f_lo=220.0, f_hi=660.0):
    """Soft sine pad whose pitch and level follow a value (a spread, an error, a score) between vmin and vmax.

    times: samples on the VIDEO timeline [s]; value: the quantity at those times. Returns (start_time, audio).
    """
    t0, t1 = times[0], times[-1]
    tt = t0 + _t(t1 - t0)
    x = np.clip((np.interp(tt, times, value) - vmin) / (vmax - vmin + 1e-12), 0, 1)
    f = f_lo * (f_hi / f_lo) ** x                           # exponential = musical pitch
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
    shimmer = 1 + 0.08 * np.sin(2 * np.pi * 5.0 * tt)
    fade = np.minimum(1, np.minimum((tt - t0) / 0.2, (t1 - tt) / 0.4))
    return t0, 0.14 * tone * (0.5 + 0.5 * x) * shimmer * fade


# ------------------------------------------------------------------ voice pronunciation
# Kokoro's dictionary gets some technical words wrong. Each entry maps the phonemes it produces to the correct
# ones; finalize() applies them to every voice line (and passes phonemes to Kokoro only when a fix applies).
# Find a word's phonemes with: Kokoro(...).tokenizer.phonemize("word", "en-us")
PRONUNCIATION = {
    "kˈɑːvɛɹˌiəns": "kˌoʊvˈɛɹiəns",   # covariance: co-VAIR-iance, not KAH-variance
    "ˈaɪdʒən": "ˈaɪɡən",             # eigen(vector, value, ...): hard g, EYE-gen
}


def speak(tts, text, voice="am_michael", speed=1.05, lang="en-us"):
    """Kokoro TTS with the PRONUNCIATION fixes applied."""
    ph = tts.tokenizer.phonemize(text, lang)
    fixed = ph
    for wrong, right in PRONUNCIATION.items():
        fixed = fixed.replace(wrong, right)
    if fixed == ph:
        return tts.create(text, voice=voice, speed=speed, lang=lang)
    return tts.create(fixed, voice=voice, speed=speed, lang=lang, is_phonemes=True)


# ------------------------------------------------------------------ assembly
def load_cues(path):
    return json.loads(pathlib.Path(path).read_text())


def build_track(duration, events, layers=()):
    """events: [(time, name or array)], layers: [(start_time, array)] -> mono float array."""
    out = np.zeros(int((duration + 2) * SR))
    for t, what in list(events) + list(layers):
        clip = ONE_SHOTS[what]() if isinstance(what, str) else what
        s = int(max(t, 0) * SR)
        e = min(s + len(clip), len(out))
        out[s:e] += clip[: e - s]
    return out[: int(duration * SR)]


def finalize(silent_mp4, out_mp4, sfx=None, voice_lines=None, voice="am_michael", speed=1.05,
             kokoro_dir=None, sfx_gain_db=-6.0):
    """Mix effects (+ optional voiceover lines [(start, text)]) and mux onto the silent video."""
    silent_mp4, out_mp4 = pathlib.Path(silent_mp4), pathlib.Path(out_mp4)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(silent_mp4)], capture_output=True, text=True, check=True).stdout)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        tracks = []
        if sfx is not None:
            sfx = 0.5 * sfx / (np.abs(sfx).max() + 1e-9)       # peak at -6 dBFS before gain
            sf.write(tmp / "sfx.wav", sfx, SR)
            tracks.append(("sfx", tmp / "sfx.wav", sfx_gain_db))
        if voice_lines:
            from kokoro_onnx import Kokoro
            kd = pathlib.Path(kokoro_dir or ".")
            tts = Kokoro(str(kd / "kokoro-v1.0.onnx"), str(kd / "voices-v1.0.bin"))
            vo = np.zeros(int((dur + 2) * SR))
            prev_end = 0.0
            for i, (start, text) in enumerate(voice_lines):
                a, sr = speak(tts, text, voice=voice, speed=speed)
                if sr != SR:
                    a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
                assert start >= prev_end, f"voice line {i} starts at {start}s, previous runs until {prev_end:.2f}s"
                prev_end = start + len(a) / SR
                print(f"voice line {i}: {start:5.1f}s -> {prev_end:5.1f}s")
                s = int(start * SR)
                vo[s:s + len(a)] += a
            sf.write(tmp / "vo.wav", vo[: int(dur * SR)], SR)
            tracks.append(("vo", tmp / "vo.wav", 0.0))
        inputs, chains, labels = [], [], []
        for i, (name, path, gain) in enumerate(tracks):
            inputs += ["-i", str(path)]
            norm = "loudnorm=I=-16:TP=-1.5," if name == "vo" else ""
            chains.append(f"[{i + 1}:a]{norm}volume={gain}dB[{name}]")
            labels.append(f"[{name}]")
        chains.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,alimiter=limit=0.89[mix]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent_mp4), *inputs,
                        "-filter_complex", ";".join(chains), "-map", "0:v", "-map", "[mix]",
                        "-c:v", "copy", "-bsf:v", "h264_metadata=sample_aspect_ratio=1/1",
                        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)], check=True)
    print("wrote", out_mp4)
