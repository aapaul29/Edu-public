"""Shared look for every video: vertical 9:16 frame, dark background, one palette.

Usage at the top of a scene file:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from common.style import *          # brings in manim + palette + vertical()
    vertical()                          # 1080x1920, frame 9 x 16
"""
import json
import pathlib

from manim import *  # noqa: F401,F403

# Palette
BG = "#0E1116"
FG = "#E8EAED"
MUTED = "#8A93A3"
ACCENT = "#4FC3F7"   # main highlight (blue)
ACCENT_2 = "#FFB74D"  # secondary (orange)
GOOD = "#81C784"
BAD = "#E57373"

# TikTok/Reels safe zone in scene units (frame is 9 x 16, 120 px per unit). On a phone, TikTok zooms the
# 9:16 video to fill a taller screen (crops ~4% off each side), the status bar + tabs cover the top ~14%,
# the caption/username/music block covers the bottom ~15%, and the like/comment/share column sits on
# the right. Keep ALL text and key visuals inside this box, centered on x = 0.
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 5.6, -4.6, -2.8, 2.8
SAFE_CX = 0.0
SAFE_CY = (SAFE_TOP + SAFE_BOTTOM) / 2          # 0.5
TITLE_Y = 5.3                                   # where titles go

FONT = "Inter"  # clean sans; manim falls back to the system default if missing

# Font sizes tuned for a 9-unit-wide vertical frame (text renders ~1.6x larger than in 16:9)
TITLE, SUBTITLE, BODY, SMALL = 30, 26, 24, 20


def vertical(fps: int = 30, height: int = 1920) -> None:
    """Configure manim for TikTok/Reels/Shorts (9:16)."""
    config.pixel_height = height
    config.pixel_width = height * 9 // 16
    config.frame_height = 16.0
    config.frame_width = 9.0
    config.frame_rate = fps
    config.background_color = BG
    Text.set_default(font=FONT)


def caption(text: str, size: int = BODY, color: str = FG) -> Text:
    """On-screen caption for videos without voiceover."""
    return Text(text, font_size=size, color=color, line_spacing=0.9)


# ------------------------------------------------------------------ sound cues
_CUES = []


def cue(scene, name, **info):
    """Log a sound-effect cue at the scene's current time (call right before self.play)."""
    _CUES.append({"t": round(scene.renderer.time, 3), "name": name, **info})


def save_cues(path):
    """Write the cues to a JSON file (call at the end of construct)."""
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_CUES, indent=1))
