"""Why a spinning phone flips: the tennis racket theorem (intermediate axis theorem).

MuJoCo simulates and renders the phone (phone_sim.py); this Manim scene plays those frames and adds the
overlays, then explains the theory: Euler's equations, the linearized wobble and its growth rate, and the
picture on the angular-momentum sphere. Pauses are sized from the measured voiceover lines (voice.py).

Render (from the repo root):
    MUJOCO_GL=egl python videos/physics/tennis-racket-theorem/scenes/phone_sim.py      # frames, once
    manim -qh videos/physics/tennis-racket-theorem/scenes/tennis_racket.py TennisRacket
"""
import json
import pathlib
import sys

import numpy as np
from PIL import Image
from scipy.integrate import solve_ivp

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3]))
sys.path.insert(0, str(HERE))
from common.style import *  # noqa: E402,F403
from phone_sim import FRAMES, FPS, FLIPS, OMEGA, EPS, RUNS, INERTIA, GROWTH  # noqa: E402
from voice import durations  # noqa: E402

vertical()

VO = durations()
GAP = 0.35                       # silence after each voiceover line

IMG_H = 6.0                      # height of the MuJoCo picture in scene units
IMG_C = np.array([SAFE_CX, 1.0, 0])
SKY = np.array([14, 17, 21])     # MuJoCo's flat skybox comes out 1 level off BG; snap it to BG exactly
BG_RGB = np.array([int(BG[i:i + 2], 16) for i in (1, 3, 5)])
I1, I2, I3 = INERTIA


def load(path):
    a = np.array(Image.open(path).convert("RGBA"))
    near = np.abs(a[..., :3].astype(int) - SKY).max(axis=-1) <= 2
    a[near, :3] = BG_RGB
    return a


class PhoneView:
    """An ImageMobject that shows MuJoCo frame round(sim_t * FPS) of the current run."""

    def __init__(self):
        self.run = "mid"
        self.st = ValueTracker(0)
        self.img = ImageMobject(load(FRAMES / "mid" / "0000.png")).scale_to_fit_height(IMG_H).move_to(IMG_C)
        self._shown = None
        self.zoom = ValueTracker(0)          # 0: full size, 1: small at the top (for the explanation)
        self.img.add_updater(lambda m: self.refresh())

    def refresh(self):
        z = self.zoom.get_value()
        self.img.scale_to_fit_height(IMG_H * (1 - 0.5 * z)).move_to(IMG_C + z * (np.array([SAFE_CX, 3.0, 0]) - IMG_C))
        if self.run == "axes":
            key = ("axes", 0)
            path = FRAMES / "axes.png"
        else:
            n = len(RUNS[self.run]["t"])
            i = int(np.clip(round(self.st.get_value() * FPS), 0, n - 1))
            key, path = (self.run, i), FRAMES / self.run / f"{i:04d}.png"
        if key != self._shown:
            self.img.pixel_array = load(path)
            self._shown = key


def flips_upto(t):
    return int(np.sum(FLIPS <= t + 1e-6))


def tex(*parts, size=1.0, color=FG):
    return MathTex(*parts, color=color).scale(size)


def fit(mob, width=SAFE_RIGHT - SAFE_LEFT - 0.2):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    return mob


# ---------------------------------------------------------------- angular-momentum sphere (polhodes)
SPH_C = np.array([SAFE_CX, -1.35, 0])
SPH_R = 2.25
_v = np.array([0.95, 1.35, 0.85])            # looking from here: all three positive axes on the front side
FWD = _v / np.linalg.norm(_v)
RIGHT = np.cross([0, 0, 1], FWD)
RIGHT /= np.linalg.norm(RIGHT)
UPV = np.cross(FWD, RIGHT)


def sph(p):
    """Unit vector in the body frame (long, middle, screen) -> (scene point, depth; depth > 0 is the front)."""
    p = np.asarray(p, float)
    return SPH_C + SPH_R * np.array([p @ RIGHT, p @ UPV, 0]), p @ FWD


def polhode(l0, t_max=60.0):
    """One closed path of the angular-momentum direction (body frame), torque-free: dL/dt = L x (L / I)."""
    inertia = INERTIA / INERTIA.max()          # rescaled: only the shape of the path matters, not its speed

    def rhs(_, L):
        return np.cross(L, L / inertia)

    sol = solve_ivp(rhs, (0, t_max), l0, rtol=1e-9, atol=1e-11, max_step=0.05, dense_output=True)
    ts = np.linspace(0, t_max, 6000)
    pts = sol.sol(ts).T
    d = np.linalg.norm(pts - pts[0], axis=1)
    far = np.argmax(d > 0.2)                  # leave the start, then come back
    back = far + np.argmin(d[far:far + 4000])
    return pts[: back + 1]


def sphere_paths(pts, color, width=3, front=0.95, behind=0.22):
    """Polyline on the sphere, split into front and back pieces (back drawn faint)."""
    xy, depth = zip(*(sph(p) for p in pts))
    xy, depth = np.array(xy), np.array(depth)
    out = VGroup()
    start = 0
    for i in range(1, len(pts) + 1):
        if i == len(pts) or np.sign(depth[i]) != np.sign(depth[start]):
            seg = xy[max(start - 1, 0): i]
            if len(seg) >= 2:
                op = front if depth[start] > 0 else behind
                out.add(VMobject(stroke_color=color, stroke_width=width, stroke_opacity=op).set_points_as_corners(seg))
            start = i
    return out


def great_circle(normal, color, width=4):
    n = np.asarray(normal, float) / np.linalg.norm(normal)
    a = np.cross(n, [0, 1, 0])
    a /= np.linalg.norm(a)
    b = np.cross(n, a)
    th = np.linspace(0, 2 * np.pi, 400)
    return sphere_paths([np.cos(x) * a + np.sin(x) * b for x in th], color, width)


class TennisRacket(Scene):
    def construct(self):
        pv = PhoneView()
        st = pv.st
        self.vo_end = 0.0

        def now():
            return self.renderer.time

        def say(line, dt=0.0):
            """Start voiceover line `line` dt seconds from now (make_audio.py places it at this cue)."""
            cue(self, "vo", line=line, dt=dt)
            self.vo_end = now() + dt + VO[line]

        def left():
            """Seconds until the current line has finished (plus a short gap)."""
            return max(0.0, self.vo_end + GAP - now())

        def hold(minimum=0.1):
            self.wait(max(minimum, left()))

        def advance(to, *anims, first_flip_sound="tick"):
            """Play the simulation in real time up to sim time `to`, with a tick on every flip."""
            t0 = st.get_value()
            for k, f in enumerate(FLIPS if pv.run == "mid" else []):
                if t0 < f <= to + 1e-9:
                    sound = first_flip_sound if k == 0 and first_flip_sound else "tick"
                    cue(self, sound, dt=float(f - t0))
            self.play(st.animate.set_value(to), *anims, run_time=to - t0, rate_func=linear)

        def advance_past_voice(minimum_to=0.0):
            advance(max(minimum_to, st.get_value() + left()))

        def spin_sound(run, sim_from, sim_to):
            cue(self, "spin", run=run, sim_from=sim_from, sim_to=sim_to)

        def at(y, mob):
            return mob.move_to([SAFE_CX, y, 0])

        def swap(old, new):
            """Cross-fade one text into another in the same spot (morphing letters looks garbled)."""
            return [FadeOut(old, shift=UP * 0.15), FadeIn(new, shift=UP * 0.15)]

        # ------------------------------------------------ hook: it flips within 2 s
        title = Text("Why does a spinning phone flip?", font_size=TITLE, color=FG, weight=BOLD)
        title.scale_to_fit_width(min(title.width, SAFE_RIGHT - SAFE_LEFT)).move_to([SAFE_CX, TITLE_Y, 0])
        cap = at(-3.2, caption("Toss a phone end over end..."))
        self.add(pv.img)
        hook_end = 0.3 + VO["hook"] + GAP
        spin_sound("mid", 0.0, hook_end)
        say("hook", dt=0.3)
        cue(self, "whoosh")
        advance(0.6, FadeIn(title, shift=DOWN * 0.3), FadeIn(cap))
        advance(1.25)
        cue(self, "pop")
        cap2_ = at(-3.2, caption("...and it flips itself over!", BODY, ACCENT_2))
        advance(1.75, *swap(cap, cap2_))
        cap = cap2_
        advance(hook_end)

        # ------------------------------------------------ the three axes
        pv.run = "axes"
        tips = json.loads((FRAMES / "axes.json").read_text())
        s = IMG_H / 720

        def px(p):
            return IMG_C + np.array([(p[0] - 360) * s, (360 - p[1]) * s, 0])

        def clamp(mob):
            dx = max(0, mob.get_right()[0] - SAFE_RIGHT) - max(0, SAFE_LEFT - mob.get_left()[0])
            return mob.shift(LEFT * dx)

        lab_long = Text("long axis", font_size=SMALL, color=FG).next_to(px(tips["long"][1]), UP, buff=0.12)
        lab_mid = clamp(Text("middle axis", font_size=SMALL, color=FG).next_to(px(tips["mid"][0]), DOWN, buff=0.18))
        lab_scr = clamp(Text("screen axis", font_size=SMALL, color=FG)
                        .next_to(px(tips["screen"][0]), DOWN, buff=0.15).shift(LEFT * 0.55))  # clear of the phone
        labels = VGroup(lab_long, lab_mid, lab_scr)
        say("axes")
        cue(self, "whoosh")
        cap3_ = at(-3.2, caption("Every phone has 3 spin axes"))
        self.play(*swap(cap, cap3_), FadeIn(labels, lag_ratio=0.3), run_time=0.7)
        hold()
        cap = cap3_

        # ------------------------------------------------ 1 and 2: stable
        rows_y = [-2.75, -3.3, -3.85]

        def row(i, name, verdict, color):
            lt = Text(f"{i}  {name}", font_size=BODY, color=FG)
            rt = Text(verdict, font_size=BODY, color=color, weight=BOLD)
            lt.move_to([SAFE_LEFT + 0.35 + lt.width / 2, rows_y[i - 1], 0])
            rt.move_to([SAFE_RIGHT - 0.35 - rt.width / 2, rows_y[i - 1], 0])
            return VGroup(lt, rt)

        seg_y = 4.5
        rows = VGroup()
        seg = None
        for i, (run, name) in enumerate((("long", "long axis"), ("screen", "screen axis")), start=1):
            new_seg = Text(f"{i}. Spin it around the {name}", font_size=BODY, color=FG)
            new_seg.scale_to_fit_width(min(new_seg.width, SAFE_RIGHT - SAFE_LEFT)).move_to([SAFE_CX, seg_y, 0])
            pv.run = run
            st.set_value(0)
            seg_end = max(3.4, 0.1 + VO[run] + GAP)
            spin_sound(run, 0.0, seg_end)
            say(run, dt=0.1)
            cue(self, "whoosh")
            if seg is None:
                advance(0.5, FadeOut(labels), FadeOut(cap), FadeIn(new_seg, shift=DOWN * 0.2))
            else:
                advance(0.5, *swap(seg, new_seg))
            seg = new_seg
            advance(2.0)
            r = row(i, name.capitalize(), "steady", GOOD)
            rows.add(r)
            cue(self, "pop")
            advance(2.4, FadeIn(r, shift=UP * 0.15))
            advance(seg_end)

        # ------------------------------------------------ 3: the middle axis flips
        pv.run = "mid"
        st.set_value(0)
        counter = always_redraw(lambda: Text(f"flips: {flips_upto(st.get_value())}", font_size=BODY,
                                             color=BAD if flips_upto(st.get_value()) else MUTED)
                                .move_to([SAFE_CX, seg_y - 0.5, 0]))
        new_seg = Text("3. Spin it around the middle axis", font_size=BODY, color=FG)
        new_seg.scale_to_fit_width(min(new_seg.width, SAFE_RIGHT - SAFE_LEFT)).move_to([SAFE_CX, seg_y, 0])
        mid_end = 8.0
        spin_sound("mid", 0.0, mid_end)
        cue(self, "riser", dt=0.2)
        say("mid", dt=0.3)
        advance(0.5, *swap(seg, new_seg), FadeIn(counter))
        seg = new_seg
        advance(FLIPS[0], first_flip_sound="wrong")
        r3 = row(3, "Middle axis", "flips!", BAD)
        rows.add(r3)
        advance(FLIPS[0] + 0.4, FadeIn(r3, shift=UP * 0.15))
        advance(mid_end)

        # ------------------------------------------------ why: moments of inertia, the middle one is unstable
        bars_x0, bars_len = -0.75, 2.9
        names = ("long", "middle", "screen")
        header = at(1.15, Text("How hard is each axis to spin?", font_size=SMALL, color=MUTED))
        bar_rows = VGroup()
        bars = VGroup()
        for k, (nm, I) in enumerate(zip(names, INERTIA)):
            y = 0.55 - 0.55 * k
            lab = Text(nm, font_size=BODY, color=FG)
            lab.move_to([bars_x0 - 0.2 - lab.width / 2, y, 0])
            bar = Rectangle(width=bars_len * I / INERTIA.max(), height=0.32, fill_color=MUTED, fill_opacity=1,
                            stroke_width=0)
            bar.move_to([bars_x0 + bar.width / 2, y, 0])
            bars.add(bar)
            bar_rows.add(VGroup(lab, bar))
        unstable = at(-1.15, caption("The one in between flips", BODY, ACCENT_2))

        t_sim = st.get_value()
        say("inertia", dt=0.2)
        why_from = st.get_value()
        why_to = why_from + 0.2 + VO["inertia"] + GAP + VO["wobble"] + GAP + 0.6
        spin_sound("mid", why_from, why_to)
        cue(self, "whoosh")
        advance(t_sim + 0.8, FadeOut(seg), FadeOut(counter), FadeOut(rows), pv.zoom.animate.set_value(1))
        cue(self, "pop")
        advance(t_sim + 2.0, FadeIn(header), *[GrowFromEdge(r, LEFT) for r in bar_rows])
        advance(t_sim + 4.6)                          # "...the middle axis sits in between"
        cue(self, "pop")
        advance(t_sim + 5.6, bars[0].animate.set_fill(GOOD), bars[2].animate.set_fill(GOOD),
                bars[1].animate.set_fill(BAD), FadeIn(unstable))
        advance_past_voice()

        # live plot of the spin about the middle axis: + means one way, - means flipped
        x_end = why_to
        ax = Axes(x_range=[0, x_end, 5], y_range=[-1.1, 1.1, 1], x_length=4.9, y_length=1.5, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False})
        ax.move_to([SAFE_CX + 0.25, -2.75, 0])
        plus = Text("+", font_size=SMALL, color=MUTED).next_to(ax.c2p(0, 1), LEFT, buff=0.15)
        minus = Text("–", font_size=SMALL, color=MUTED).next_to(ax.c2p(0, -1), LEFT, buff=0.15)
        plot_lab = at(-1.75, Text("spin around the middle axis", font_size=SMALL, color=MUTED))
        mid = RUNS["mid"]

        def curve():
            t = min(st.get_value(), x_end)
            m = mid["t"] <= t
            pts = [ax.c2p(a, b) for a, b in zip(mid["t"][m], mid["w"][m, 1] / OMEGA)]
            if len(pts) < 2:
                pts = [ax.c2p(0, 1), ax.c2p(0.01, 1)]
            return VMobject(stroke_color=ACCENT_2, stroke_width=4).set_points_smoothly(pts)

        trace = always_redraw(curve)
        cap2 = at(-4.05, caption("A tiny wobble grows, then flips it"))
        say("wobble")
        cue(self, "pop")
        self.add(trace)
        t_sim = st.get_value()
        advance(t_sim + 1.0, FadeIn(VGroup(ax, plus, minus, plot_lab)))
        cue(self, "pop")
        advance(t_sim + 1.8, FadeIn(cap2))
        advance(max(why_to, st.get_value() + left()))
        t_resume = st.get_value()

        # ------------------------------------------------ theory 1: Euler's equations
        cue(self, "whoosh")
        trace.clear_updaters()
        self.play(FadeOut(VGroup(header, bar_rows, unstable, ax, plus, minus, plot_lab, cap2, trace)),
                  FadeOut(pv.img), run_time=0.6)
        pv.img.suspend_updating()

        def euler_eq(lhs, br, a, b, w=1.0):
            return tex(lhs, "=", br, a, b, size=w)

        e1 = euler_eq(r"I_1\,\dot\omega_1", r"(I_2-I_3)", r"\,\omega_2", r"\,\omega_3")
        e2 = euler_eq(r"I_2\,\dot\omega_2", r"(I_3-I_1)", r"\,\omega_3", r"\,\omega_1")
        e3 = euler_eq(r"I_3\,\dot\omega_3", r"(I_1-I_2)", r"\,\omega_1", r"\,\omega_2")
        eqs = VGroup(e1, e2, e3)
        for k, e in enumerate(eqs):
            e.move_to([SAFE_CX, 3.75 - 0.85 * k, 0])
            e.shift(RIGHT * (eqs[0][1].get_center()[0] - e[1].get_center()[0]))     # align the = signs
        th_head = at(4.6, Text("Euler's equations, no torque", font_size=SMALL, color=MUTED))
        legend = VGroup(Text("1 long   2 middle   3 screen", font_size=SMALL, color=MUTED),
                        tex(r"I_1 < I_2 < I_3", size=0.75, color=MUTED)).arrange(DOWN, buff=0.22)
        at(0.95, legend)
        say("euler", dt=0.1)
        cue(self, "pop")
        self.play(FadeIn(th_head), run_time=0.5)
        self.play(LaggedStart(*[Write(e) for e in eqs], lag_ratio=0.35), run_time=2.4)
        cue(self, "pop")
        self.play(FadeIn(legend, shift=UP * 0.15), run_time=0.6)
        hold(0.5)

        # ------------------------------------------------ theory 2: linearize around a middle-axis spin
        spin_def = tex(r"\omega_2 \approx \Omega", r",\quad", r"\omega_1,\ \omega_3\ \text{tiny}", size=0.85)
        spin_def[0].set_color(ACCENT_2)
        spin_def[2].set_color(ACCENT)
        at(0.0, spin_def)
        say("linear", dt=0.1)
        cue(self, "pop")
        self.play(FadeOut(legend), FadeIn(spin_def, shift=UP * 0.15), run_time=0.7)
        self.wait(1.4)
        l1 = euler_eq(r"I_1\,\dot\omega_1", r"(I_2-I_3)", r"\,\Omega", r"\,\omega_3").move_to(e1)
        l3 = euler_eq(r"I_3\,\dot\omega_3", r"(I_1-I_2)", r"\,\omega_1", r"\,\Omega").move_to(e3)
        l1[2].set_color(ACCENT_2)
        l3[3].set_color(ACCENT_2)
        l1.shift(e1[1].get_center() - l1[1].get_center())
        l3.shift(e3[1].get_center() - l3[1].get_center())
        cue(self, "tick")
        self.play(TransformMatchingTex(e1, l1), TransformMatchingTex(e3, l3), run_time=1.0)
        self.wait(max(0.2, 4.4 - 3.2))
        box = SurroundingRectangle(VGroup(e2[3], e2[4]), color=BAD, buff=0.08, stroke_width=3)
        tiny = Text("tiny × tiny", font_size=SMALL, color=BAD).next_to(box, RIGHT, buff=0.15)
        fit(tiny, SAFE_RIGHT - box.get_right()[0] - 0.2)
        cue(self, "pop")
        self.play(Create(box), FadeIn(tiny), run_time=0.6)
        self.wait(1.4)
        zero = tex(r"\approx 0", size=1.0, color=BAD).next_to(e2[1], RIGHT, buff=0.2)
        cue(self, "thump")
        self.play(FadeOut(VGroup(e2[2:], box, tiny)), FadeIn(zero), e2[:2].animate.set_color(MUTED), run_time=0.7)
        cap_zero = at(-0.85, Text("so ω₂ stays ≈ Ω", font_size=SMALL, color=MUTED))
        self.play(FadeIn(cap_zero), run_time=0.4)
        hold(0.3)

        # ------------------------------------------------ theory 3: one equation for the wobble
        say("combine", dt=0.1)
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(e2[:2], zero, spin_def, cap_zero)),
                  l1.animate.move_to([SAFE_CX, 3.85, 0]), l3.animate.move_to([SAFE_CX, 3.05, 0]), run_time=0.7)
        arrow = Arrow([SAFE_CX, 2.55, 0], [SAFE_CX, 1.95, 0], color=MUTED, buff=0, stroke_width=4,
                      max_tip_length_to_length_ratio=0.35)
        res = tex(r"\ddot\omega_1", "=", r"\Omega^2\,", r"{(I_3-I_2)", r"(I_2-I_1)", r"\over I_1 I_3}", r"\,\omega_1",
                  size=1.0)
        at(1.05, fit(res))
        cue(self, "pop")
        self.play(GrowArrow(arrow), Write(res), run_time=1.4)
        self.wait(max(0.2, 3.3 - 2.2))
        br1, br2 = res[3], res[4]
        pos1 = tex(r">0", size=0.7, color=GOOD).next_to(br1, UP, buff=0.12)
        pos2 = tex(r">0", size=0.7, color=GOOD).next_to(br2, UP, buff=0.12)
        cue(self, "pop")
        self.play(br1.animate.set_color(GOOD), br2.animate.set_color(GOOD), FadeIn(pos1), FadeIn(pos2), run_time=0.6)
        self.wait(0.9)
        grow = tex(r"=\lambda^2\,\omega_1", r"\;\Rightarrow\;", r"\omega_1 \propto e^{\lambda t}", size=0.95)
        grow[2].set_color(BAD)
        at(-0.35, grow)
        grows = at(-1.05, Text("grows exponentially", font_size=BODY, color=BAD, weight=BOLD))
        cue(self, "riser")
        self.play(FadeIn(grow, shift=UP * 0.15), run_time=0.7)
        cue(self, "wrong")
        self.play(FadeIn(grows, shift=UP * 0.1), run_time=0.4)
        hold(0.3)

        # ------------------------------------------------ theory 4: the other two axes oscillate
        say("stable", dt=0.1)
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(l1, l3, arrow, pos1, pos2, th_head)),
                  VGroup(res, grow, grows).animate.scale(0.75).move_to([SAFE_CX, 3.35, 0]), run_time=0.7)
        mid_lab = Text("middle", font_size=SMALL, color=BAD)
        mid_lab.next_to(VGroup(res, grow, grows), UP, buff=0.18)

        def case(label, lhs, frac, w, y):
            lab = Text(label, font_size=SMALL, color=FG)
            eq = tex(lhs, "=", r"-", r"\Omega^2\,", frac, w, size=0.9)
            fit(eq)
            VGroup(lab, eq).arrange(DOWN, buff=0.2).move_to([SAFE_CX, y, 0])
            return lab, eq

        lab_l, eq_l = case("long axis", r"\ddot\omega_2", r"{(I_2-I_1)(I_3-I_1) \over I_2 I_3}", r"\,\omega_2", 0.75)
        lab_s, eq_s = case("screen axis", r"\ddot\omega_1", r"{(I_3-I_1)(I_3-I_2) \over I_1 I_2}", r"\,\omega_1", -1.55)
        cue(self, "pop")
        self.play(FadeIn(mid_lab), FadeIn(VGroup(lab_l, eq_l), shift=UP * 0.15), run_time=0.7)
        cue(self, "pop")
        self.play(FadeIn(VGroup(lab_s, eq_s), shift=UP * 0.15), run_time=0.7)
        self.wait(max(0.2, 3.4 - 1.5))
        cue(self, "tick")
        self.play(Indicate(eq_l[2], color=GOOD, scale_factor=1.8), Indicate(eq_s[2], color=GOOD, scale_factor=1.8),
                  run_time=0.8)
        eq_l[2].set_color(GOOD)
        eq_s[2].set_color(GOOD)
        osc = at(-3.15, Text("minus sign: the wobble oscillates", font_size=SMALL, color=GOOD))
        steady = at(-3.75, Text("steady", font_size=BODY, color=GOOD, weight=BOLD))
        self.wait(0.6)
        cue(self, "chime")
        self.play(FadeIn(osc, shift=UP * 0.1), FadeIn(steady, shift=UP * 0.1), run_time=0.6)
        hold(0.3)

        # ------------------------------------------------ theory 5: the numbers for this phone, vs the simulation
        say("numbers", dt=0.1)
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(res, grow, grows, mid_lab, lab_l, eq_l, lab_s, eq_s, osc, steady)), run_time=0.6)
        lam = tex(r"\lambda", "=", r"\Omega\sqrt{(I_3-I_2)(I_2-I_1) \over I_1 I_3}", size=0.95)
        at(4.15, lam)
        lam_num = tex(r"\lambda = 4.9\ \text{s}^{-1}", size=1.0, color=ACCENT_2)
        lam_note = Text("this phone, 1 turn per second", font_size=SMALL, color=MUTED)
        VGroup(lam_num, lam_note).arrange(DOWN, buff=0.18).move_to([SAFE_CX, 2.55, 0])
        cue(self, "pop")
        self.play(FadeIn(lam, shift=UP * 0.15), run_time=0.6)
        cue(self, "pop")
        self.play(FadeIn(lam_num), FadeIn(lam_note), run_time=0.6)

        # log plot: wobble size sqrt(w1^2 + w3^2) / Omega, simulation vs the growing solution of the linear model
        T_LOG = 1.8
        lg = Axes(x_range=[0, T_LOG, 0.5], y_range=[-3, 0.3, 1], x_length=4.6, y_length=3.6, tips=False,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False})
        lg.move_to([SAFE_CX + 0.35, -0.85, 0])
        yl = VGroup(*[tex(lbl, size=0.55, color=MUTED).next_to(lg.c2p(0, e), LEFT, buff=0.15)
                      for e, lbl in ((-3, r"0.001"), (-2, r"0.01"), (-1, r"0.1"), (0, r"1"))])
        grid = VGroup(*[DashedLine(lg.c2p(0, e), lg.c2p(T_LOG, e), color=MUTED, stroke_width=1, stroke_opacity=0.35,
                                   dash_length=0.06) for e in (-3, -2, -1, 0)])
        xl = Text("time (s)", font_size=SMALL, color=MUTED).next_to(lg.c2p(T_LOG / 2, -3), DOWN, buff=0.2)
        yt = Text("wobble", font_size=SMALL, color=MUTED).next_to(lg.c2p(0, 0.3), UP, buff=0.15).shift(RIGHT * 0.2)
        m = mid["t"] <= T_LOG
        amp = np.hypot(mid["w"][m, 0], mid["w"][m, 2]) / OMEGA
        sim_curve = VMobject(stroke_color=ACCENT_2, stroke_width=5).set_points_smoothly(
            [lg.c2p(t, np.log10(a)) for t, a in zip(mid["t"][m], amp)])
        # growing mode of  w1' = a w3, w3' = b w1  started from w1 = w3 = EPS * Omega
        a_ = OMEGA * (I2 - I3) / I1
        c_plus = EPS * (1 + a_ / GROWTH) / 2
        amp_plus = abs(c_plus) * np.hypot(1, GROWTH / a_)
        t_th = np.linspace(0, T_LOG, 50)
        y_th = np.log10(amp_plus) + GROWTH * t_th / np.log(10)
        keep = y_th <= 0.3
        th_line = DashedLine(lg.c2p(t_th[keep][0], y_th[keep][0]), lg.c2p(t_th[keep][-1], y_th[keep][-1]),
                             color=FG, stroke_width=3, dash_length=0.1)
        leg_sim = Text("simulation", font_size=SMALL, color=ACCENT_2)
        leg_sim.next_to(lg.c2p(1.05, np.log10(np.interp(1.05, mid["t"][m], amp))), DR, buff=0.12)
        leg_th = tex(r"\text{theory: } e^{\lambda t}", size=0.65, color=FG)
        leg_th.next_to(lg.c2p(0.95, np.log10(amp_plus) + GROWTH * 0.95 / np.log(10)), UL, buff=0.12)
        legend2 = VGroup(leg_sim, leg_th)
        cue(self, "pop")
        self.play(FadeIn(VGroup(lg, yl, grid, xl, yt)), run_time=0.6)
        cue(self, "riser", dt=0.4)
        self.play(Create(th_line), FadeIn(leg_th), run_time=1.0)
        self.play(Create(sim_curve), FadeIn(leg_sim), run_time=2.6, rate_func=linear)
        cue(self, "chime")
        self.play(Indicate(sim_curve, color=ACCENT_2, scale_factor=1.0), run_time=0.6)
        hold(0.3)

        # ------------------------------------------------ theory 6: the angular-momentum sphere
        say("sphere", dt=0.1)
        cue(self, "whoosh")
        self.play(FadeOut(VGroup(lam, lam_num, lam_note, lg, yl, grid, xl, yt, sim_curve, th_line, legend2)),
                  run_time=0.6)
        st.set_value(t_resume)
        pv.img.resume_updating()
        pv.img.set_opacity(0)
        self.add(pv.img)
        sph_from = t_resume
        sph_to = sph_from + 0.8 + VO["sphere"] + 0.1 + GAP + VO["saddle"] + GAP + 1.5
        spin_sound("mid", sph_from, sph_to)

        outline = Circle(radius=SPH_R, color=MUTED, stroke_width=2).move_to(SPH_C)
        th_s = np.arctan(np.sqrt((1 / I1 - 1 / I2) / (1 / I2 - 1 / I3)))   # separatrix angle in the long-screen plane
        loops_long, loops_screen = VGroup(), VGroup()
        for th in np.linspace(0.12, th_s - 0.1, 3):
            for sgn in (1, -1):
                loops_long.add(sphere_paths(polhode(sgn * np.array([np.cos(th), 0, np.sin(th)])), MUTED, 2.5))
        for th in np.linspace(th_s + 0.1, np.pi / 2 - 0.12, 3):
            for sgn in (1, -1):
                loops_screen.add(sphere_paths(polhode(sgn * np.array([np.cos(th), 0, np.sin(th)])), MUTED, 2.5))
        k_s = np.tan(th_s)
        separatrix = VGroup(great_circle([-k_s, 0, 1], MUTED, 3), great_circle([k_s, 0, 1], MUTED, 3))
        axis_dots, axis_labs = VGroup(), VGroup()
        for k, (nm, direction) in enumerate((("long", RIGHT), ("middle", UP), ("screen", LEFT))):
            p, _ = sph(np.eye(3)[k])
            axis_dots.add(Dot(p, radius=0.06, color=FG))
            axis_labs.add(Text(nm, font_size=SMALL, color=FG).next_to(p, direction, buff=0.12))
        axis_labs[1].shift(RIGHT * 0.35)

        def spin_dir(t):
            i = int(np.clip(round(t * FPS), 0, len(mid["t"]) - 1))
            L = INERTIA * mid["w"][i]
            return L / np.linalg.norm(L), i

        def marker():
            l, _ = spin_dir(st.get_value())
            p, d = sph(l)
            return Dot(p, radius=0.11, color=ACCENT_2, fill_opacity=1.0 if d > 0 else 0.35)

        def trail():
            t = st.get_value()
            _, i = spin_dir(t)
            i0 = max(0, i - int(1.6 * FPS))
            pts = [INERTIA * w / np.linalg.norm(INERTIA * w) for w in mid["w"][i0:i + 1]]
            if len(pts) < 2:
                return VGroup()
            return sphere_paths(pts, ACCENT_2, width=5, front=0.9, behind=0.3)

        dot = always_redraw(marker)
        tr = always_redraw(trail)
        sph_cap = at(-4.1, Text("energy and angular momentum are conserved", font_size=SMALL, color=MUTED))
        fit(sph_cap)
        cue(self, "pop")
        advance(sph_from + 0.8, pv.img.animate.set_opacity(1), FadeIn(outline), FadeIn(axis_dots),
                FadeIn(axis_labs))
        self.add(tr, dot)
        t0 = st.get_value()
        advance(t0 + 4.4, FadeIn(sph_cap))
        cue(self, "whoosh")
        advance(t0 + 6.4, *[Create(g) for g in (*loops_long, *loops_screen, *separatrix)])
        advance_past_voice()

        say("saddle", dt=0.1)
        t0 = st.get_value()
        cue(self, "pop")
        advance(t0 + 1.0, loops_long.animate.set_color(GOOD), loops_screen.animate.set_color(GOOD))
        advance(t0 + 3.4)
        saddle = Text("saddle", font_size=SMALL, color=BAD, weight=BOLD)
        saddle.next_to(axis_dots[1], DOWN, buff=0.2).shift(LEFT * 0.1)
        cue(self, "pop")
        advance(t0 + 4.2, separatrix.animate.set_color(BAD), FadeIn(saddle), axis_labs[1].animate.set_color(BAD))
        advance(max(sph_to, st.get_value() + left()))

        # ------------------------------------------------ outro
        name = at(-2.55, Text("The tennis racket theorem", font_size=SUBTITLE, color=ACCENT, weight=BOLD))
        aka = at(-3.15, Text("works for rackets, books and phones", font_size=SMALL, color=MUTED))
        tryit = at(-3.85, caption("Try it with your phone. Over a bed.", BODY, FG))
        t0 = st.get_value()
        out_to = t0 + 0.7 + VO["outro"] + 1.0
        spin_sound("mid", t0, out_to)
        cue(self, "whoosh")
        tr.clear_updaters()
        dot.clear_updaters()
        advance(t0 + 0.7, FadeOut(VGroup(outline, loops_long, loops_screen, separatrix, axis_dots, axis_labs,
                                         saddle, sph_cap, tr, dot)), pv.zoom.animate.set_value(0))
        say("outro")
        cue(self, "chime")
        advance(t0 + 1.4, FadeIn(name, shift=UP * 0.2))
        cue(self, "pop")
        advance(t0 + 2.4, FadeIn(aka), FadeIn(tryit))
        advance(max(out_to, st.get_value() + left() + 0.6))
        save_cues(HERE.parent / "renders" / "tennis_racket_theorem_cues.json")
