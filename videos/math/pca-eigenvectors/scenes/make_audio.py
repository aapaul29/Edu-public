"""Build the soundtrack: procedural effects + AI voiceover, muxed onto the silent render.

Steps (from the repo root):
    manim -qh videos/math/pca-eigenvectors/scenes/pca.py PCAEigen
        -> copy the mp4 to renders/pca_eigenvectors_silent.mp4 (the scene also writes the cue file)
    KOKORO_DIR=/path/to/kokoro/models python videos/math/pca-eigenvectors/scenes/make_audio.py
        -> renders/pca_eigenvectors.mp4

Kokoro model files: github.com/thewh1teagle/kokoro-onnx, release "model-files-v1.0".
"""
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE))
from common import sfx  # noqa: E402

RENDERS = HERE.parent / "renders"
NAME = "pca_eigenvectors"

# (start time in the video [s], line). Start times = BEATS in pca.py; each line fits before the next beat.
VOICE_LINES = [
    (0.3, "This is how a computer sees handwriting. Every digit is an eight by eight image: sixty four numbers."),
    (7.5, "So each image is a point in sixty four D. But most of those numbers move together."),
    (13.4, "Take two small patches, one at the top and one at the bottom. When one has ink, the other usually does too."),
    (20.6, "PCA finds new axes, where a few numbers capture most of the variation. First, subtract the mean."),
    (28.2, "Spin a line through the center, and project every image onto it. The spread is the variance the line keeps."),
    (35.6, "The best line keeps the most variance, and leaves the smallest errors. That's principal component one."),
    (42.3, "Stack the centered data in a matrix X. Its covariance is X transpose X, over n."),
    (48.7, "PC one is the top eigenvector of that matrix. Its eigenvalue is exactly that variance."),
    (56.0, "In practice, PCA uses the SVD. X equals U, S, V transpose."),
    (62.0, "V rotates the cloud onto its principal axes. S is how far it stretches along each one. And U holds every image's new coordinates."),
    (71.9, "Plug that into the covariance, and V holds the eigenvectors. Each variance is sigma squared, over n."),
    (79.3, "Now use all sixty four pixels. The principal components are images themselves: eigen digits."),
    (86.3, "Mix a few of them with the right weights, and the digit comes back. Ten components already keep three quarters of the variance."),
    (94.2, "And with just two numbers per image, the ten digits sort themselves into groups. PCA never saw a label."),
    (101.5, "That's PCA: center, take the SVD, keep the top directions."),
]


def effects(duration):
    events, layers = [], []
    for c in sfx.load_cues(RENDERS / f"{NAME}_cues.json"):
        if c["name"] == "spread":                 # pitch follows the variance while the line spins
            layers.append(sfx.tone_follow(c["times"], c["values"], c["vmin"], c["vmax"]))
            continue
        events.append((c["t"] + c.get("dt", 0.0), c["name"]))
    return sfx.build_track(duration, events, layers)


if __name__ == "__main__":
    silent = RENDERS / f"{NAME}_silent.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(silent)], capture_output=True, text=True).stdout)
    track = effects(dur)
    sfx.finalize(silent, RENDERS / f"{NAME}.mp4", sfx=track, voice_lines=VOICE_LINES,
                 kokoro_dir=os.environ.get("KOKORO_DIR"), sfx_gain_db=-6.0)
    # effects-only version (no voice), handy if you'd rather record yourself
    sfx.finalize(silent, RENDERS / f"{NAME}_sfx_only.mp4", sfx=track, sfx_gain_db=-3.0)
