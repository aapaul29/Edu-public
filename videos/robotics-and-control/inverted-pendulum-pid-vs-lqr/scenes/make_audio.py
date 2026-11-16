"""Build the soundtrack for the cart-pole video: procedural effects only (no voiceover).

From the repo root:
    manim -qh videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle
        -> copy the mp4 to renders/inverted_pendulum_pid_vs_lqr_silent.mp4 (the scene also writes the cue file)
    python videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/make_audio.py
        -> renders/inverted_pendulum_pid_vs_lqr.mp4
"""
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE))
from common import sfx  # noqa: E402
from cartpole import TRAJ, FMAX, EDGE  # noqa: E402  (same simulation as the video)

RENDERS = HERE.parent / "renders"
NAME = "inverted_pendulum_pid_vs_lqr"


def effects(duration):
    cues = sfx.load_cues(RENDERS / f"{NAME}_cues.json")
    events, layers = [], []
    pid = TRAJ["pid"]
    t_off = pid[np.argmax(np.abs(pid[:, 1]) > EDGE), 0]      # sim time the PID cart runs away (view starts following)
    for c in cues:
        if c["name"] == "motors":
            for ctrl in ("pid", "lqr"):
                r = TRAJ[ctrl]
                m = (r[:, 0] >= c["sim_from"]) & (r[:, 0] <= c["sim_to"])
                video_t = c["t"] + (r[m, 0] - c["sim_from"]) * c["run_time"] / (c["sim_to"] - c["sim_from"])
                layers.append(sfx.motor_whir(video_t, r[m, 5], FMAX))
            if c["sim_from"] <= t_off <= c["sim_to"]:
                events.append((c["t"] + (t_off - c["sim_from"]) * c["run_time"] / (c["sim_to"] - c["sim_from"]),
                               "whoosh"))
                events.append((events[-1][0] + 0.25, "wrong"))
        else:
            events.append((c["t"] + c.get("dt", 0.0), c["name"]))
    return sfx.build_track(duration, events, layers)


if __name__ == "__main__":
    silent = RENDERS / f"{NAME}_silent.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(silent)], capture_output=True, text=True).stdout)
    sfx.finalize(silent, RENDERS / f"{NAME}.mp4", sfx=effects(dur), sfx_gain_db=0.0)
