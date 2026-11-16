"""Approximate how a 1080x1920 video looks inside the TikTok app on a phone.

Grabs frames at the given times, crops the sides like TikTok's zoom-to-fill, and shades
the areas covered by the app's UI (status bar + tabs, caption block, button column).
Anything important inside a shaded area, or touching the image edge, will be hidden or cramped.

    python common/phone_preview.py path/to/video.mp4 2 8 15 30 -o preview.png
"""
import argparse
import subprocess
import tempfile
import pathlib

W, H = 1080, 1920
CROP = 0.04                      # fraction cropped from EACH side by zoom-to-fill
TOP, BOTTOM = 0.14, 0.15         # fraction of height covered at the top / bottom
BUTTONS_X, BUTTONS_Y0, BUTTONS_Y1 = 0.86, 0.45, 0.88   # right-hand button column (of cropped width / height)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("times", nargs="+", type=float)
    ap.add_argument("-o", "--out", default="phone_preview.png")
    a = ap.parse_args()
    cw = int(W * (1 - 2 * CROP))
    shade = (f"crop={cw}:{H}:{int(W * CROP)}:0,"
             f"drawbox=x=0:y=0:w={cw}:h={int(H * TOP)}:color=red@0.4:t=fill,"
             f"drawbox=x=0:y={int(H * (1 - BOTTOM))}:w={cw}:h={int(H * BOTTOM)}:color=red@0.4:t=fill,"
             f"drawbox=x={int(cw * BUTTONS_X)}:y={int(H * BUTTONS_Y0)}:w={cw - int(cw * BUTTONS_X)}:"
             f"h={int(H * (BUTTONS_Y1 - BUTTONS_Y0))}:color=red@0.4:t=fill,scale=320:-1")
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i, t in enumerate(a.times):
            f = pathlib.Path(tmp) / f"{i:02d}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", a.video, "-frames:v", "1",
                            "-vf", shade, str(f)], check=True)
            frames.append(f)
        args = sum((["-i", str(f)] for f in frames), [])
        subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex",
                        f"hstack=inputs={len(frames)}" if len(frames) > 1 else "null", a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
