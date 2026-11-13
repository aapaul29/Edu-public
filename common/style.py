"""Shared look for every video: vertical 9:16 frame, dark background, one palette.

Usage at the top of a scene file:

    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
    from common.style import *          # brings in manim + palette + vertical()
    vertical()                          # 1080x1920, frame 9 x 16
"""
from manim import *  # noqa: F401,F403

# Palette
BG = "#0E1116"
FG = "#E8EAED"
MUTED = "#8A93A3"
ACCENT = "#4FC3F7"   # main highlight (blue)
ACCENT_2 = "#FFB74D"  # secondary (orange)
GOOD = "#81C784"
BAD = "#E57373"

FONT = "Inter"  # clean sans; manim falls back to the system default if missing

# Font sizes tuned for a 9-unit-wide vertical frame (text renders ~1.6x larger than in 16:9)
TITLE, SUBTITLE, BODY, SMALL = 36, 28, 26, 20


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
