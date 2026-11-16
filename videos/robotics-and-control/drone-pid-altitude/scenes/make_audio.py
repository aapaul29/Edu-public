"""Build the soundtrack: procedural effects + AI voiceover, muxed onto the silent render.

Steps (from the repo root):
    manim -qh videos/robotics-and-control/drone-pid-altitude/scenes/drone_pid.py DronePID
        -> copy the mp4 to renders/drone_pid_altitude_silent.mp4 (the scene also writes the cue file)
    KOKORO_DIR=/path/to/kokoro/models python videos/robotics-and-control/drone-pid-altitude/scenes/make_audio.py
        -> renders/drone_pid_altitude.mp4

Kokoro model files: github.com/thewh1teagle/kokoro-onnx, release "model-files-v1.0".
"""
import os
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE))
from common import sfx  # noqa: E402
from drone_pid import RUNS, MASS, G  # noqa: E402  (same simulation as the video)

RENDERS = HERE.parent / "renders"
NAME = "drone_pid_altitude"

# (start time in the video [s], line). Start times follow the scene timing in drone_pid.py.
VOICE_LINES = [
    (0.3, "How does a drone know how hard to push, to hover at exactly three metres?"),
    (5.3, "Start simple. Push harder the farther you are from the target. That's P."),
    (9.9, "But it bounces, and hovers too low. Right at the target, the error is zero, "
          "so the thrust would be zero too."),
    (17.1, "So add I. Keep adding up the error over time, until the sag is gone."),
    (22.3, "It reaches three metres. And overshoots. And overshoots again."),
    (27.5, "Last, add D. If you're closing in fast, brake."),
    (32.3, "Smooth. No overshoot. Right on target."),
    (38.8, "P is the present error. I is the past. D is where the error is heading. That's PID."),
]


def effects(duration):
    cues = sfx.load_cues(RENDERS / f"{NAME}_cues.json")
    events, layers = [], []
    for c in cues:
        if c["name"] == "hum":
            r = RUNS[c["run"]]                                  # columns: t, z, u
            video_t = c["t"] + r[:, 0] * c["run_time"] / c["sim_time"]
            layers.append(sfx.rotor_hum(video_t, r[:, 2], MASS * G))
        else:
            events.append((c["t"], c["name"]))
    return sfx.build_track(duration, events, layers)


if __name__ == "__main__":
    silent = RENDERS / f"{NAME}_silent.mp4"
    import subprocess
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(silent)], capture_output=True, text=True).stdout)
    track = effects(dur)
    sfx.finalize(silent, RENDERS / f"{NAME}.mp4", sfx=track, voice_lines=VOICE_LINES,
                 kokoro_dir=os.environ.get("KOKORO_DIR"), sfx_gain_db=-6.0)
    # effects-only version (no voice), handy if you'd rather record yourself
    sfx.finalize(silent, RENDERS / f"{NAME}_sfx_only.mp4", sfx=track, sfx_gain_db=-3.0)
