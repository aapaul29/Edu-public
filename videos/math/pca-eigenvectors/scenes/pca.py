"""How PCA works: variance, eigenvectors and the SVD, on real handwritten digits.

Data: 1,797 handwritten digits, 8x8 pixels with ink 0-16 (UCI "Optical Recognition of Handwritten Digits",
the copy that ships with scikit-learn), stored in digits.csv next to this file.
  1. Every image is 64 numbers = a point in 64D, and neighbouring parts of the image move together.
  2. 2D example: ink in a 2x2 patch at the top vs a 2x2 patch at the bottom of the same column.
     Center, spin a line, measure the variance it keeps -> PC 1.
  3. PC 1 is the top eigenvector of the covariance X^T X / n, and its eigenvalue is that variance.
  4. The SVD X = U S V^T: V rotates onto the principal axes, S is the stretch, U the new coordinates.
  5. All 64 pixels: eigen-digits, rebuilding a digit from k components, and 2D clusters of the 10 digits.

Render from the repo root:
    manim -qh videos/math/pca-eigenvectors/scenes/pca.py PCAEigen
"""
import csv
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
from common.style import *  # noqa: E402,F403

vertical()

# ---------------------------------------------------------------- data
with open(HERE / "digits.csv") as f:
    _rows = list(csv.reader(f))[1:]
X64 = np.array([[float(v) for v in r[:64]] for r in _rows])
LABELS = np.array([int(r[64]) for r in _rows])
N = len(X64)
IMGS = X64.reshape(-1, 8, 8)

# 2D example: mean ink of a 2x2 patch at the top (rows 0-1) and at the bottom (rows 6-7), columns 2-3
TOP_PATCH, BOT_PATCH = (slice(0, 2), slice(2, 4)), (slice(6, 8), slice(2, 4))
RAW = np.c_[IMGS[:, 0:2, 2:4].mean(axis=(1, 2)), IMGS[:, 6:8, 2:4].mean(axis=(1, 2))]
MEAN = RAW.mean(axis=0)
XC = RAW - MEAN                       # centered data matrix X (N x 2)
COV = XC.T @ XC / N
_, S_, VT_ = np.linalg.svd(XC, full_matrices=False)
V1 = VT_[0] * np.sign(VT_[0, 0])
V2 = np.array([-V1[1], V1[0]])
L1, L2 = S_ ** 2 / N
THETA1 = np.arctan2(V1[1], V1[0])
SCORES = np.c_[XC @ V1, XC @ V2]      # = U S

SHOW = np.random.default_rng(0).choice(N, 350, replace=False)   # images drawn in the 2D plot (stats use all N)

# all 64 pixels
MEAN64 = X64.mean(axis=0)
XC64 = X64 - MEAN64
_, S64, VT64 = np.linalg.svd(XC64, full_matrices=False)
EV64 = S64 ** 2 / N
CUM64 = np.cumsum(EV64) / EV64.sum()
Z64 = XC64 @ VT64[:2].T
DEMO = int(np.where(LABELS == 3)[0][2])            # the digit we rebuild
KS = [1, 2, 5, 10, 20, 64]
DIGIT_COLORS = [ACCENT, ACCENT_2, GOOD, BAD, "#BA68C8", "#F06292", "#4DB6AC", "#FFF176", "#BCAAA4", "#90A4AE"]


def spread(theta):
    u = np.array([np.cos(theta), np.sin(theta)])
    return float(u @ COV @ u)


TH_START, TH_SWEEP = THETA1 + np.deg2rad(75), THETA1 - np.deg2rad(45)
SWEEP_T, SETTLE_T = 4.8, 1.6

# ---------------------------------------------------------------- layout
C = np.array([0.0, 2.1, 0.0])         # plot center
K = 0.24                              # scene units per ink unit (2D example)
O_RAW = np.array([-1.95, 0.25, 0.0])  # origin of the raw (uncentered) axes
R_LINE = 2.6
READ_Y, METER_Y = -0.85, -1.25
Y1, Y2, Y3 = -1.6, -2.95, -3.75
KZ = 0.08                             # scene units per unit for the 64D -> 2D plot
PIX_BG = "#1C222B"

# Voiceover beats [s]; each line's measured length fits before the next beat (see make_audio.py)
BEATS = [0.3, 7.5, 13.4, 20.6, 28.2, 35.6, 42.3, 48.7, 56.0, 62.0, 71.9, 79.3, 86.3, 94.2, 101.5]
END = 108.0


def at(p, k=K):
    return C + np.array([k * p[0], k * p[1], 0.0])


def raw_at(p):
    return O_RAW + np.array([K * p[0], K * p[1], 0.0])


def dots_at(points, color=FG, opacity=0.85, k=K, colors=None, r=0.05):
    return VGroup(*[Dot(at(p, k), radius=r, color=(colors[i] if colors else color), fill_opacity=opacity)
                    for i, p in enumerate(points)])


def direction(theta):
    return np.array([np.cos(theta), np.sin(theta)])


def digit_image(vals, cell, center, mode="ink", vmax=16.0):
    """8x8 image as squares. mode 'ink': dark -> white. mode 'signed': negative orange, positive blue."""
    vals = np.asarray(vals, float).reshape(8, 8)
    g = VGroup()
    for i in range(8):
        for j in range(8):
            v = vals[i, j]
            if mode == "ink":
                col = interpolate_color(ManimColor(PIX_BG), ManimColor(FG), float(np.clip(v / vmax, 0, 1)))
            else:
                a = float(np.clip(abs(v) / vmax, 0, 1))
                col = interpolate_color(ManimColor(PIX_BG), ManimColor(ACCENT if v > 0 else ACCENT_2), a)
            sq = Square(cell, stroke_width=0, fill_color=col, fill_opacity=1)
            sq.move_to(np.array(center) + np.array([(j - 3.5) * cell, (3.5 - i) * cell, 0]))
            g.add(sq)
    return g


def patch_box(img_mob, patch, color):
    (r0, r1), (c0, c1) = (patch[0].start, patch[0].stop), (patch[1].start, patch[1].stop)
    cells = VGroup(*[img_mob[i * 8 + j] for i in range(r0, r1) for j in range(c0, c1)])
    return SurroundingRectangle(cells, color=color, buff=0.02, stroke_width=4)


def reconstruct(k):
    z = XC64[DEMO] @ VT64[:k].T
    return np.clip(MEAN64 + z @ VT64[:k], 0, 16)


class PCAEigen(Scene):
    def wait_until(self, t):
        dt = t - self.renderer.time
        assert dt > -1e-6, f"timeline overrun: at {self.renderer.time:.2f}s, wanted {t}s"
        if dt > 1e-3:
            self.wait(dt)

    def construct(self):
        print(f"N={N} mean={MEAN.round(2)} cov={COV.round(2).tolist()} S={S_.round(1)} l1={L1:.2f} l2={L2:.2f} "
              f"pc1={np.rad2deg(THETA1):.1f} deg kept2d={L1 / (L1 + L2):.3f} cum64={ {k: round(CUM64[k - 1], 3) for k in KS} }")
        title = Text("How PCA works", font_size=TITLE, color=FG, weight=BOLD).move_to([SAFE_CX, TITLE_Y, 0])

        # ---- 0: a grid of real handwritten digits
        cell = 0.11
        picks = [int(np.where(LABELS == d)[0][1]) for d in range(10)] + [int(np.where(LABELS == d)[0][5]) for d in (2, 5, 8, 0, 7)]
        grid = VGroup(*[digit_image(IMGS[p], cell, [(-2.24 + 1.12 * (i % 5)), 4.0 - 1.15 * (i // 5), 0])
                        for i, p in enumerate(picks)])
        cue(self, "whoosh")
        self.play(FadeIn(title, shift=DOWN * 0.2), LaggedStart(*[FadeIn(g, scale=0.8) for g in grid], lag_ratio=0.06),
                  run_time=1.6)
        self.wait_until(BEATS[0] + 3.4)
        sel = grid[3]
        box = SurroundingRectangle(sel, color=ACCENT_2, buff=0.06)
        info = VGroup(Text("8 × 8 pixels = 64 numbers", font_size=BODY, color=FG),
                      Text("each pixel: ink from 0 to 16", font_size=SMALL, color=MUTED)).arrange(DOWN, buff=0.15)
        info.move_to([SAFE_CX, Y1 + 0.1, 0])
        cue(self, "pop")
        self.play(Create(box), FadeIn(info, shift=UP * 0.15), run_time=0.7)

        # ---- 1: a point in 64D, numbers move together
        self.wait_until(BEATS[1])
        pt = MathTex(r"\text{1 image} = (x_1, x_2, \dots, x_{64}) \in \mathbb{R}^{64}", color=FG).scale(0.75)
        pt.move_to([SAFE_CX, Y2 - 0.1, 0])
        cue(self, "pop")
        self.play(FadeIn(pt, shift=UP * 0.15), run_time=0.6)

        # ---- 2: two patches, top and bottom
        self.wait_until(BEATS[2])
        big = digit_image(IMGS[picks[3]], 0.3, C + UP * 0.1)
        b_top, b_bot = patch_box(big, TOP_PATCH, ACCENT), patch_box(big, BOT_PATCH, ACCENT_2)
        self.play(FadeOut(VGroup(info, pt, box)), FadeTransform(sel.copy(), big), FadeOut(grid), run_time=0.9)
        l_top = Text("top patch", font_size=SMALL, color=ACCENT).next_to(big, LEFT, buff=0.25).match_y(b_top)
        l_bot = Text("bottom patch", font_size=SMALL, color=ACCENT_2).next_to(big, LEFT, buff=0.25).match_y(b_bot)
        cue(self, "tick")
        self.play(Create(b_top), Create(b_bot), FadeIn(l_top), FadeIn(l_bot), run_time=0.7)
        self.wait_until(BEATS[2] + 3.6)
        ax_x = Arrow(raw_at([0, 0]), raw_at([16.5, 0]), buff=0, color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.03)
        ax_y = Arrow(raw_at([0, 0]), raw_at([0, 16.5]), buff=0, color=MUTED, stroke_width=3, max_tip_length_to_length_ratio=0.03)
        ticks = VGroup(*[Text(str(i), font_size=16, color=MUTED).next_to(raw_at([i, 0]), DOWN, buff=0.08) for i in (0, 8, 16)],
                       *[Text(str(i), font_size=16, color=MUTED).next_to(raw_at([0, i]), LEFT, buff=0.08) for i in (8, 16)])
        lab_x = Text("ink in top patch", font_size=SMALL, color=ACCENT).next_to(raw_at([8, 0]), DOWN, buff=0.38)
        lab_y = Text("ink in bottom patch", font_size=SMALL, color=ACCENT_2).next_to(raw_at([0, 16.5]), UP, buff=0.1).align_to(ax_y, LEFT)
        raw_axes = VGroup(ax_x, ax_y, ticks, lab_x, lab_y)
        dots = VGroup(*[Dot(raw_at(RAW[i]), radius=0.045, color=FG, fill_opacity=0.8) for i in SHOW])
        n_lab = Text(f"each dot = one image ({len(SHOW)} of {N} shown)", font_size=SMALL, color=MUTED).move_to([SAFE_CX, Y1 + 0.2, 0])
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(big, b_top, b_bot, l_top, l_bot)), FadeIn(raw_axes),
                  LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.004), FadeIn(n_lab), run_time=1.4)

        # ---- 3: goal + center
        self.wait_until(BEATS[3])
        goal = Text("goal: new axes where a few numbers\nkeep most of the variation", font_size=SMALL, color=FG,
                    line_spacing=0.9).move_to([SAFE_CX, Y1, 0])
        cue(self, "pop")
        self.play(FadeOut(n_lab), FadeIn(goal, shift=UP * 0.15), run_time=0.6)
        self.wait_until(BEATS[3] + 5.0)
        mean_mark = VGroup(Line(LEFT * 0.15, RIGHT * 0.15), Line(DOWN * 0.15, UP * 0.15)).set_stroke(BAD, 4).move_to(raw_at(MEAN))
        center_eq = MathTex(r"x \;\leftarrow\; x - \bar{x}", color=FG).scale(0.8).move_to([SAFE_CX, Y2, 0])
        mean_lab = MathTex(r"\bar{x} = (%.2f,\ %.2f)" % tuple(MEAN), color=BAD).scale(0.65).move_to([SAFE_CX, Y3, 0])
        cue(self, "tick")
        self.play(FadeIn(mean_mark, scale=1.5), Write(center_eq), FadeIn(mean_lab), run_time=0.7)
        cross = VGroup(Line(at([-12, 0]), at([12, 0])), Line(at([0, -10.5]), at([0, 10.5]))).set_stroke(MUTED, 1.5, 0.5)
        cue(self, "whoosh")
        self.play(Transform(dots, dots_at(XC[SHOW], r=0.045, opacity=0.8)), mean_mark.animate.move_to(C),
                  FadeOut(raw_axes), FadeIn(cross), run_time=1.0)
        self.play(FadeOut(mean_mark), run_time=0.3)

        # ---- 4: spin a line
        self.wait_until(BEATS[4])
        th = ValueTracker(TH_START)

        def line_mob():
            u = direction(th.get_value())
            return Line(at(-R_LINE / K * u), at(R_LINE / K * u), color=ACCENT_2, stroke_width=4)

        def projections():
            u = direction(th.get_value())
            g = VGroup()
            for p in XC[SHOW]:
                q = (p @ u) * u
                g.add(Line(at(p), at(q), color=ACCENT_2, stroke_width=1, stroke_opacity=0.3))
                g.add(Dot(at(q), radius=0.03, color=ACCENT_2))
            return g

        def readout():
            v = spread(th.get_value())
            txt = Text(f"variance kept by the line: {v:.2f}", font_size=SMALL, color=FG).move_to([SAFE_CX, READ_Y, 0])
            track = Line([-2.4, METER_Y, 0], [2.4, METER_Y, 0], color=MUTED, stroke_width=6, stroke_opacity=0.35)
            bar = Line([-2.4, METER_Y, 0], [-2.4 + 4.8 * v / (L1 * 1.04), METER_Y, 0], color=ACCENT_2, stroke_width=6)
            return VGroup(txt, track, bar)

        spin_line, proj, meter = always_redraw(line_mob), always_redraw(projections), always_redraw(readout)
        cue(self, "tick")
        self.play(FadeOut(VGroup(goal, center_eq, mean_lab)), Create(spin_line), FadeIn(proj), FadeIn(meter), run_time=0.6)
        t0 = self.renderer.time
        ts = np.linspace(0, SWEEP_T + SETTLE_T, 120)
        sm = np.vectorize(smooth)
        ang = np.where(ts <= SWEEP_T, TH_START + (TH_SWEEP - TH_START) * sm(np.clip(ts / SWEEP_T, 0, 1)),
                       TH_SWEEP + (THETA1 - TH_SWEEP) * sm(np.clip((ts - SWEEP_T) / SETTLE_T, 0, 1)))
        cue(self, "spread", times=(t0 + ts).round(3).tolist(), values=[round(spread(a), 4) for a in ang],
            vmin=round(L2, 4), vmax=round(L1, 4))
        self.play(th.animate.set_value(TH_SWEEP), run_time=SWEEP_T, rate_func=smooth)
        self.play(th.animate.set_value(THETA1), run_time=SETTLE_T, rate_func=smooth)
        spin_line.clear_updaters()
        proj.clear_updaters()
        meter.clear_updaters()

        # ---- 5: max variance = min error -> PC 1
        self.wait_until(BEATS[5])
        mm = MathTex(r"\max \text{ variance} \;=\; \min \textstyle\sum \text{error}^2", color=FG).scale(0.75).move_to([SAFE_CX, Y1 - 0.15, 0])
        errs = VGroup(*[proj[i] for i in range(0, len(proj), 2)])
        cue(self, "pop")
        self.play(FadeIn(mm, shift=UP * 0.15), errs.animate.set_stroke(BAD, width=1.5, opacity=0.8), run_time=0.8)
        self.wait_until(BEATS[5] + 4.3)
        pc1 = Line(at(-R_LINE / K * V1), at(R_LINE / K * V1), color=ACCENT, stroke_width=6)
        pc1_lab = Text("PC 1", font_size=SMALL, color=ACCENT, weight=BOLD).move_to(at(10.0 * V1 - 2.0 * V2))
        cue(self, "chime")
        self.play(ReplacementTransform(spin_line, pc1), FadeIn(pc1_lab, scale=0.8), meter[0].animate.set_color(ACCENT),
                  meter[2].animate.set_color(ACCENT), FadeOut(proj), run_time=0.7)

        # ---- 6: data matrix and covariance
        self.wait_until(BEATS[6])
        xdef = MathTex(r"X:\ \text{centered data},\ %d \times 2" % N, color=FG).scale(0.7).move_to([SAFE_CX, Y1 - 0.1, 0])
        cov = MathTex(r"\Sigma = \frac{X^\top X}{n} = \begin{bmatrix}%.2f & %.2f\\ %.2f & %.2f\end{bmatrix}"
                      % (COV[0, 0], COV[0, 1], COV[1, 0], COV[1, 1]), color=FG).scale(0.75).move_to([SAFE_CX, Y2 - 0.2, 0])
        cue(self, "whoosh")
        self.play(FadeOut(mm), dots.animate.set_opacity(0.3), Write(xdef), run_time=0.9)
        self.wait_until(BEATS[6] + 3.6)
        self.play(Write(cov), run_time=1.0)

        # ---- 7: PC 1 = top eigenvector, eigenvalue = variance
        self.wait_until(BEATS[7])
        arr = Arrow(C, at(3.0 * V1), buff=0, color=ACCENT, stroke_width=7)
        arr_l = Arrow(C, at(0.5 * L1 * V1), buff=0, color=ACCENT, stroke_width=7)
        eig = MathTex(r"\Sigma v_1 = \lambda_1 v_1", color=ACCENT).scale(0.8).move_to([-1.2, Y3 - 0.4, 0])
        lam = MathTex(r"\lambda_1 = %.2f" % L1, color=ACCENT).scale(0.8).move_to([1.5, Y3 - 0.4, 0])
        cue(self, "pop")
        self.play(GrowArrow(arr), Write(eig), run_time=0.8)
        self.play(Transform(arr, arr_l), run_time=0.8)
        self.wait_until(BEATS[7] + 4.2)
        cue(self, "tick")
        self.play(FadeIn(lam, shift=UP * 0.15), Indicate(meter[0], color=ACCENT, scale_factor=1.08), run_time=0.9)

        # ---- 8: the SVD
        self.wait_until(BEATS[8])
        svd = MathTex(r"X", r"=", r"U", r"S", r"V^\top", color=FG).scale(1.1)
        svd.arrange(RIGHT, buff=0.45, aligned_edge=DOWN).move_to([SAFE_CX, Y1 - 0.05, 0])
        dims = VGroup(*[Text(t, font_size=18, color=MUTED).next_to(svd[i], DOWN, buff=0.18)
                        for i, t in ((0, f"{N}×2"), (2, f"{N}×2"), (3, "2×2"), (4, "2×2"))])
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(xdef, cov, eig, lam, meter, arr)), Write(svd), run_time=1.0)
        self.play(FadeIn(dims), run_time=0.5)

        # ---- 9: V rotates, S stretches, U = new coordinates
        self.wait_until(BEATS[9])
        v_val = MathTex(r"V^\top:\ \text{rotation by } %.1f^\circ" % np.rad2deg(THETA1), color=ACCENT_2).scale(0.7).move_to([SAFE_CX, Y2 - 0.1, 0])
        cue(self, "whoosh")
        self.play(svd[4].animate.set_color(ACCENT_2), dots.animate.set_opacity(0.8), FadeIn(v_val), run_time=0.5)
        self.play(Transform(dots, dots_at(SCORES[SHOW], r=0.045, opacity=0.8)), Rotate(pc1, -THETA1, about_point=C),
                  pc1_lab.animate.move_to(at([-9.5, -5.6])), run_time=1.6)
        self.wait_until(BEATS[9] + 3.1)
        s_val = MathTex(r"S = \mathrm{diag}(%.1f,\ %.1f)" % tuple(S_), color=GOOD).scale(0.7).move_to([SAFE_CX, Y3 - 0.05, 0])
        sx = DoubleArrow(at([-np.sqrt(L1) * 2, -8.6]), at([np.sqrt(L1) * 2, -8.6]), buff=0, color=GOOD, stroke_width=4, tip_length=0.15)
        sy = DoubleArrow(at([10.3, -np.sqrt(L2) * 2]), at([10.3, np.sqrt(L2) * 2]), buff=0, color=GOOD, stroke_width=4, tip_length=0.15)
        cue(self, "pop")
        self.play(svd[4].animate.set_color(FG), svd[3].animate.set_color(GOOD), FadeIn(s_val), GrowFromCenter(sx), GrowFromCenter(sy),
                  run_time=0.8)
        self.wait_until(BEATS[9] + 6.2)
        u_note = Text("U: every image's new coordinates", font_size=SMALL, color=ACCENT).move_to([SAFE_CX, Y3 - 0.55, 0])
        cue(self, "tick")
        self.play(svd[3].animate.set_color(FG), svd[2].animate.set_color(ACCENT), FadeIn(u_note),
                  Indicate(dots, color=ACCENT, scale_factor=1.03), run_time=0.9)

        # ---- 10: why V holds the eigenvectors
        self.wait_until(BEATS[10])
        link = MathTex(r"\frac{X^\top X}{n} = V\,\frac{S^2}{n}\,V^\top", color=FG).scale(0.75).move_to([SAFE_CX, Y2 - 0.15, 0])
        lam_svd = MathTex(r"\lambda_1 = \frac{\sigma_1^2}{n} = \frac{%.1f^2}{%d} = %.2f" % (S_[0], N, L1),
                          color=ACCENT).scale(0.65).move_to([SAFE_CX, Y3 - 0.42, 0])
        cue(self, "pop")
        self.play(svd[2].animate.set_color(FG), FadeOut(VGroup(v_val, s_val, u_note, sx, sy)),
                  Transform(dots, dots_at(XC[SHOW], r=0.045, opacity=0.5)), Rotate(pc1, THETA1, about_point=C),
                  pc1_lab.animate.move_to(at(10.0 * V1 - 2.0 * V2)), Write(link), run_time=1.2)
        self.wait_until(BEATS[10] + 4.0)
        cue(self, "tick")
        self.play(FadeIn(lam_svd, shift=UP * 0.15), run_time=0.7)

        # ---- 11: all 64 pixels -> eigen-digits
        self.wait_until(BEATS[11])
        heading = Text("all 64 pixels", font_size=SUBTITLE, color=FG, weight=BOLD).move_to([SAFE_CX, 4.45, 0])
        ecell = 0.115
        xs = [-2.3, -1.15, 0.0, 1.15, 2.3]
        mean_img = digit_image(MEAN64, ecell, [xs[0], 3.25, 0])
        eig_imgs = [digit_image(VT64[i], ecell, [xs[i + 1], 3.25, 0], mode="signed", vmax=np.abs(VT64[:4]).max() * 0.8)
                    for i in range(4)]
        e_labs = VGroup(*[Text(t, font_size=18, color=MUTED).move_to([x, 2.55, 0])
                          for t, x in zip(["mean", "PC 1", "PC 2", "PC 3", "PC 4"], xs)])
        e_note = Text("eigen-digits", font_size=SMALL, color=ACCENT).move_to([SAFE_CX, 2.1, 0])
        cue(self, "riser")
        self.play(FadeOut(VGroup(svd, dims, link, lam_svd, pc1, pc1_lab, cross, dots)), run_time=0.8)
        cue(self, "whoosh")
        self.play(FadeIn(heading), FadeIn(mean_img), LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in eig_imgs], lag_ratio=0.25),
                  FadeIn(e_labs), run_time=1.6)
        self.wait_until(BEATS[11] + 4.6)
        cue(self, "pop")
        self.play(FadeIn(e_note, shift=UP * 0.1), run_time=0.5)

        # ---- 12: rebuild a digit from k components
        self.wait_until(BEATS[12])
        rc, rcen, ocen = 0.25, [-1.25, 0.15, 0], [1.45, 0.15, 0]
        recon = digit_image(reconstruct(KS[0]), rc, rcen)
        orig = digit_image(IMGS[DEMO], rc, ocen)
        r_lab = Text("rebuilt", font_size=SMALL, color=FG).next_to(recon, DOWN, buff=0.15)
        o_lab = Text("original", font_size=SMALL, color=MUTED).next_to(orig, DOWN, buff=0.15)
        recipe = MathTex(r"\hat{x} = \bar{x} + z_1\,\mathrm{PC}_1 + \dots + z_k\,\mathrm{PC}_k", color=FG).scale(0.7).move_to([SAFE_CX, -1.95, 0])

        def k_text(k):
            return VGroup(Text(f"k = {k} of 64 components", font_size=BODY, color=ACCENT),
                          Text(f"{CUM64[k - 1] * 100:.0f}% of the variance", font_size=SMALL, color=FG)
                          ).arrange(DOWN, buff=0.15).move_to([SAFE_CX, -3.3, 0])

        kt = k_text(KS[0])
        cue(self, "pop")
        self.play(FadeOut(e_note), FadeIn(recon), FadeIn(orig), FadeIn(r_lab), FadeIn(o_lab), Write(recipe), FadeIn(kt), run_time=0.9)
        step_t = [1.3, 2.4, 3.6, 4.8, 6.0]
        for k, st in zip(KS[1:], step_t):
            self.wait_until(BEATS[12] + st)
            cue(self, "tick")
            self.play(Transform(recon, digit_image(reconstruct(k), rc, rcen)), Transform(kt, k_text(k)), run_time=0.45)
        # land back on k = 10 (the number the voice quotes)
        self.wait_until(BEATS[12] + 6.9)
        self.play(Transform(recon, digit_image(reconstruct(10), rc, rcen)), Transform(kt, k_text(10)), run_time=0.4)

        # ---- 13: two numbers per image -> clusters
        self.wait_until(BEATS[13])
        axz = VGroup(Line(at([-33, 0], KZ), at([33, 0], KZ)), Line(at([0, -31], KZ), at([0, 31], KZ))).set_stroke(MUTED, 1.5, 0.6)
        lzx = Text("PC 1 →", font_size=SMALL, color=MUTED).move_to(at([25, -31], KZ)).add_background_rectangle(color=BG, opacity=0.8, buff=0.05)
        lzy = Text("PC 2", font_size=SMALL, color=MUTED).move_to(at([5, 29.5], KZ)).add_background_rectangle(color=BG, opacity=0.8, buff=0.05)
        dz = dots_at(Z64, k=KZ, r=0.03, opacity=0.7)
        res = VGroup(Text("64D → 2D", font_size=BODY, color=FG, weight=BOLD),
                     Text("each image = just 2 numbers", font_size=SMALL, color=FG)).arrange(DOWN, buff=0.18).move_to([SAFE_CX, -1.6, 0])
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(heading, mean_img, *eig_imgs, e_labs, recon, orig, r_lab, o_lab, recipe, kt)), run_time=0.6)
        self.play(FadeIn(axz), FadeIn(lzx), FadeIn(lzy), LaggedStart(*[FadeIn(d) for d in dz], lag_ratio=0.0008),
                  FadeIn(res, shift=UP * 0.15), run_time=1.4)
        self.wait_until(BEATS[13] + 3.0)
        colored = dots_at(Z64, k=KZ, r=0.03, opacity=0.8, colors=[DIGIT_COLORS[l] for l in LABELS])
        tags = VGroup()
        for dgt in range(10):
            c = Z64[LABELS == dgt].mean(axis=0)
            t = Text(str(dgt), font_size=SUBTITLE, color=DIGIT_COLORS[dgt], weight=BOLD).move_to(at(c, KZ))
            t.add_background_rectangle(color=BG, opacity=0.75, buff=0.06)
            tags.add(t)
        note = Text("(PCA never saw these labels)", font_size=SMALL, color=MUTED).move_to([SAFE_CX, -2.7, 0])
        cue(self, "chime")
        self.add(lzx, lzy)   # keep the axis labels above the dots
        self.play(Transform(dz, colored), LaggedStart(*[FadeIn(t, scale=0.6) for t in tags], lag_ratio=0.08), FadeIn(note),
                  run_time=1.4)

        # ---- 14: outro
        self.wait_until(BEATS[14])
        outro = VGroup(Text("PCA =", font_size=SUBTITLE, color=FG, weight=BOLD),
                       Text("center  →  SVD  →  keep the top directions", font_size=SMALL, color=ACCENT)
                       ).arrange(DOWN, buff=0.22).move_to([SAFE_CX, -3.5, 0])
        cue(self, "pop")
        self.play(FadeIn(outro, shift=UP * 0.2), run_time=0.8)
        self.wait_until(END)
        save_cues(HERE.parent / "renders" / "pca_eigenvectors_cues.json")
