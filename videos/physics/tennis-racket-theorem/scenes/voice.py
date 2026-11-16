"""Voiceover lines for the tennis-racket video, and their measured durations.

The scene (tennis_racket.py) reads the durations to size its pauses and logs a "vo" cue wherever a line
starts; make_audio.py places each line at its cue. Edit a line here, then re-run:
    KOKORO_DIR=/path/to/kokoro/models python videos/physics/tennis-racket-theorem/scenes/voice.py
to re-measure, then re-render the scene and re-run make_audio.py.
"""
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
DURATIONS = HERE.parent / "renders" / "tennis_racket_theorem_vo.json"

LINES = {
    "hook": "Toss a phone end over end, and it flips itself over. Every single time.",
    "axes": "Every phone has three axes it can spin around.",
    "long": "Spin it around the long axis, and it stays steady.",
    "screen": "Around the axis through the screen? Also steady.",
    "mid": "But around the middle axis, it flips. And flips again.",
    "inertia": "Each axis has a moment of inertia: how hard it is to spin. The middle axis sits in between.",
    "wobble": "And that one is unstable. A tiny wobble grows, until the whole phone turns over.",
    "euler": "To see why, write down Euler's equations. They say how the spin changes when there's no torque.",
    "linear": "Spin around the middle axis at rate omega, plus a tiny wobble. "
              "Products of two small wobbles are tinier still, so drop them.",
    "combine": "Combine the two, and the wobble obeys one equation. "
               "Both brackets are positive, so it grows exponentially.",
    "stable": "Do the same for the long or the screen axis, and the sign flips. "
              "Now the wobble just oscillates, and the spin stays steady.",
    "numbers": "For this phone, lambda is four point nine per second. "
               "The wobble grows more than a hundredfold every second, just like in the simulation.",
    "sphere": "So why does it flip back? Energy and angular momentum are both conserved, "
              "so the spin can only move along these curves.",
    "saddle": "Around the stable axes, they are small loops. But the middle axis is a saddle: "
              "the path swings all the way to the other side, and back.",
    "outro": "That's the tennis racket theorem. Try it with your phone. Over a bed.",
}


def durations():
    """Measured length of each line in seconds (run this file once to measure)."""
    return json.loads(DURATIONS.read_text())


if __name__ == "__main__":
    sys.path.insert(0, str(HERE.parents[3]))
    from common import sfx
    from kokoro_onnx import Kokoro
    kd = pathlib.Path(os.environ.get("KOKORO_DIR", "."))
    tts = Kokoro(str(kd / "kokoro-v1.0.onnx"), str(kd / "voices-v1.0.bin"))
    out = {}
    for name, text in LINES.items():
        a, sr = sfx.speak(tts, text)
        out[name] = round(len(a) / sr, 2)
        print(f"{name:8s} {out[name]:5.2f}s  {text}")
    DURATIONS.parent.mkdir(parents=True, exist_ok=True)
    DURATIONS.write_text(json.dumps(out, indent=1))
    print("total", round(sum(out.values()), 1), "s ->", DURATIONS)
