"""Build the soundtrack for the tennis-racket video: procedural effects + AI voiceover.

From the repo root:
    MUJOCO_GL=egl python videos/physics/tennis-racket-theorem/scenes/phone_sim.py
    manim -qh videos/physics/tennis-racket-theorem/scenes/tennis_racket.py TennisRacket
        -> copy the mp4 to renders/tennis_racket_theorem_silent.mp4 (the scene also writes the cue file)
    KOKORO_DIR=/path/to/kokoro/models python videos/physics/tennis-racket-theorem/scenes/make_audio.py
        -> renders/tennis_racket_theorem.mp4 (voice + effects) and renders/tennis_racket_theorem_sfx_only.mp4

The voiceover text lives in voice.py; each line starts where the scene logged its "vo" cue.
Kokoro model files: github.com/thewh1teagle/kokoro-onnx, release "model-files-v1.0".
"""
import os
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE))
from common import sfx  # noqa: E402
from phone_sim import RUNS, OMEGA  # noqa: E402  (same simulation as the video)
from voice import LINES  # noqa: E402

RENDERS = HERE.parent / "renders"
NAME = "tennis_racket_theorem"
MAIN_AXIS = {"long": 0, "mid": 1, "screen": 2}
SPIN_GAIN = 0.7                      # keep the air swish well under the accents


def voice_lines():
    """[(start time in the video, text)] from the scene's "vo" cues."""
    return [(round(c["t"] + c.get("dt", 0.0), 2), LINES[c["line"]])
            for c in sfx.load_cues(RENDERS / f"{NAME}_cues.json") if c["name"] == "vo"]


def effects(duration):
    events, layers = [], []
    for c in sfx.load_cues(RENDERS / f"{NAME}_cues.json"):
        if c["name"] == "vo":
            continue
        if c["name"] == "spin":
            # air swish that follows the simulated tumble: pulse rate from |omega|, brighter while the
            # phone twists away from its spin axis (the flip)
            r = RUNS[c["run"]]
            m = (r["t"] >= c["sim_from"] - 1e-9) & (r["t"] <= c["sim_to"] + 1e-9)
            w = r["w"][m]
            twist = np.linalg.norm(np.delete(w, MAIN_AXIS[c["run"]], axis=1), axis=1) / OMEGA
            video_t = c["t"] + (r["t"][m] - c["sim_from"])          # the scene plays the sim in real time
            t0, a = sfx.spin_swish(video_t, np.linalg.norm(w, axis=1), OMEGA, brightness=twist)
            layers.append((t0, SPIN_GAIN * a))
            continue
        events.append((c["t"] + c.get("dt", 0.0), c["name"]))
    return sfx.build_track(duration, events, layers)


if __name__ == "__main__":
    silent = RENDERS / f"{NAME}_silent.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(silent)], capture_output=True, text=True).stdout)
    track = effects(dur)
    sfx.finalize(silent, RENDERS / f"{NAME}.mp4", sfx=track, voice_lines=voice_lines(),
                 kokoro_dir=os.environ.get("KOKORO_DIR"), sfx_gain_db=-6.0)
    # effects-only version (no voice), handy if you'd rather record yourself
    sfx.finalize(silent, RENDERS / f"{NAME}_sfx_only.mp4", sfx=track, sfx_gain_db=-3.0)
