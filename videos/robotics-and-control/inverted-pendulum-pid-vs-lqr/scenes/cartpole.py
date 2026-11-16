"""Balancing an inverted pendulum on a cart: PID vs LQR.

Render (from the repo root):
    manim -qh videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle
Preview:
    manim -pql videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle
"""
import pathlib
import sys

import numpy as np
from scipy.linalg import solve_continuous_are

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from common.style import *  # noqa: E402,F403

vertical()

# ---------------------------------------------------------------- physics
M, m, L, g = 1.0, 0.2, 0.6, 9.81   # cart mass, bob mass, pole length, gravity
FMAX = 25.0                        # actuator limit [N]
T_SIM, DT = 12.0, 1 / 600
TH0 = 0.3                          # initial tilt [rad] (~17 deg)
KICK_T, KICK = 6.0, 1.2            # push at t=6 s: +1.2 rad/s on the pole


def deriv(s, F):
    """Nonlinear cart-pole, theta = 0 is upright, positive = tilting right."""
    x, xd, th, thd = s
    c, sn = np.cos(th), np.sin(th)
    A = np.array([[M + m, m * L * c], [c, L]])
    b = np.array([F + m * L * thd**2 * sn, g * sn])
    xdd, thdd = np.linalg.solve(A, b)
    return np.array([xd, xdd, thd, thdd])


A_LIN = np.array([[0, 1, 0, 0],
                  [0, 0, -m * g / M, 0],
                  [0, 0, 0, 1],
                  [0, 0, (M + m) * g / (M * L), 0]])
B_LIN = np.array([[0], [1 / M], [0], [-1 / (M * L)]])
Q, R = np.diag([10, 1, 100, 1]), np.array([[0.1]])
K_LQR = (np.linalg.inv(R) @ B_LIN.T @ solve_continuous_are(A_LIN, B_LIN, Q, R)).ravel()
KP, KD, KI = 60.0, 12.0, 20.0      # PID on the angle only


def simulate(ctrl):
    s, integ, out = np.array([0.0, 0.0, TH0, 0.0]), 0.0, []
    for i in range(int(T_SIM / DT) + 1):
        t = i * DT
        if abs(t - KICK_T) < DT / 2:
            s[3] += KICK
        if ctrl == "lqr":
            F = -K_LQR @ s
        else:
            integ += s[2] * DT
            F = KP * s[2] + KD * s[3] + KI * integ
        F = float(np.clip(F, -FMAX, FMAX))
        k1 = deriv(s, F)
        k2 = deriv(s + DT / 2 * k1, F)
        k3 = deriv(s + DT / 2 * k2, F)
        k4 = deriv(s + DT * k3, F)
        out.append([t, *s, F])          # columns: t, x, xd, th, thd, F
        s = s + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return np.array(out)


TRAJ = {c: simulate(c) for c in ("pid", "lqr")}


def state(ctrl, t):
    r = TRAJ[ctrl]
    return np.interp(t, r[:, 0], r[:, 1]), np.interp(t, r[:, 0], r[:, 3])


# ---------------------------------------------------------------- drawing
POLE_LEN = 1.8     # scene units (1 unit = 1 m on the track)
FOLLOW = 2.0       # once a cart is this far from home [m], its lane's view follows it
EDGE = 2.2         # used by make_audio.py: sound cue when the PID cart clearly runs away
X0 = SAFE_CX       # track center, shifted into the safe zone
HALF_VIEW = SAFE_RIGHT - X0   # visible track on each side [m]


def cart_pole(ctrl, t, y0, color):
    x, th = state(ctrl, t)
    cam = x - float(np.clip(x, -FOLLOW, FOLLOW))   # view offset [m], 0 while the cart is near home
    xs = X0 + x - cam                               # scene x of the cart (never leaves the safe zone)
    track = Line([SAFE_LEFT, y0, 0], [SAFE_RIGHT, y0, 0], color=MUTED, stroke_width=3)
    grp = VGroup(track)
    # ground ticks every 0.5 m: they scroll past while the view follows, so the motion stays visible
    for k in np.arange(np.ceil((cam - HALF_VIEW) * 2) / 2, cam + HALF_VIEW + 1e-9, 0.5):
        sx = X0 + k - cam
        if abs(k) < 1e-6:
            continue
        h = 0.14 if abs(k - round(k)) < 1e-6 else 0.08
        grp.add(Line([sx, y0 - h, 0], [sx, y0, 0], color=MUTED, stroke_width=2))
    home_sx = X0 - cam
    if abs(home_sx - X0) <= HALF_VIEW:
        grp.add(Line([home_sx, y0 - 0.15, 0], [home_sx, y0 + 0.15, 0], color=FG, stroke_width=4))
    else:   # home has scrolled off: point back to it
        side = np.sign(x)
        arrow = Arrow([X0 - side * 1.4, y0 + 0.5, 0], [X0 - side * 2.7, y0 + 0.5, 0],
                      color=BAD, buff=0, stroke_width=6)
        lab = Text(f"home: {abs(x):.1f} m", font_size=SMALL, color=BAD).next_to(arrow, UP, buff=0.12)
        grp.add(arrow, lab)
    base = np.array([xs, y0 + 0.35, 0])
    body = RoundedRectangle(width=1.1, height=0.55, corner_radius=0.1,
                            fill_color=color, fill_opacity=1, stroke_width=0).move_to(base)
    wheels = VGroup(*[Circle(0.12, fill_color=FG, fill_opacity=1, stroke_width=0)
                      .move_to([xs + dx, y0 + 0.08, 0]) for dx in (-0.35, 0.35)])
    tip = base + POLE_LEN * np.array([np.sin(th), np.cos(th), 0])
    pole = Line(base, tip, color=FG, stroke_width=8)
    bob = Dot(tip, radius=0.16, color=ACCENT_2)
    pivot = Dot(base, radius=0.06, color=BG)
    grp.add(wheels, body, pole, pivot, bob)
    if KICK_T - 0.1 <= t <= KICK_T + 0.7:   # show the push
        grp.add(Arrow(tip + LEFT * 1.3, tip + LEFT * 0.2, color=ACCENT_2, buff=0, stroke_width=7))
    readout = Text(f"cart at x = {0.0 if abs(x) < 0.005 else x:+.2f} m", font_size=SMALL, color=MUTED).move_to([X0, y0 - 0.55, 0])
    grp.add(readout)
    return grp


class CartPoleBattle(Scene):
    def construct(self):
        y_pid, y_lqr = 1.4, -2.5

        title = Text("Balance a stick on a cart", font_size=TITLE, color=FG, weight=BOLD).move_to([SAFE_CX, TITLE_Y, 0])
        hook = caption("Same stick. Same tilt. Two controllers.", SMALL, MUTED).next_to(title, DOWN, buff=0.3)

        lab_pid = VGroup(Text("PID", font_size=SUBTITLE, color=ACCENT, weight=BOLD),
                         Text("only looks at the angle", font_size=SMALL, color=MUTED)
                         ).arrange(DOWN, buff=0.1).move_to([SAFE_CX, y_pid + 2.75, 0])
        lab_lqr = VGroup(Text("LQR", font_size=SUBTITLE, color=GOOD, weight=BOLD),
                         Text("looks at all 4 states", font_size=SMALL, color=MUTED)
                         ).arrange(DOWN, buff=0.1).move_to([SAFE_CX, y_lqr + 2.75, 0])

        t = ValueTracker(0)
        pid = always_redraw(lambda: cart_pole("pid", t.get_value(), y_pid, ACCENT))
        lqr = always_redraw(lambda: cart_pole("lqr", t.get_value(), y_lqr, GOOD))
        clock = always_redraw(lambda: Text(f"t = {t.get_value():4.1f} s", font_size=SMALL, color=MUTED)
                              .move_to([SAFE_CX, TITLE_Y - 0.5, 0]))

        cue(self, "whoosh")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=0.8)
        cue(self, "pop")
        self.play(FadeIn(hook), FadeIn(lab_pid), FadeIn(lab_lqr), FadeIn(pid), FadeIn(lqr), run_time=1.0)
        self.wait(1.2)

        cap_area = [SAFE_CX, -3.95, 0]
        cap = caption("Both catch the fall...").move_to(cap_area)
        cue(self, "pop")
        self.play(FadeOut(hook), FadeIn(cap), run_time=0.4)
        self.add(clock)
        cue(self, "motors", sim_from=0.0, sim_to=KICK_T - 0.4, run_time=KICK_T - 0.4)
        self.play(t.animate.set_value(KICK_T - 0.4), run_time=KICK_T - 0.4, rate_func=linear)

        push_cap = caption("Now give both a push.", BODY, ACCENT_2).move_to(cap_area)
        cue(self, "pop")
        self.play(Transform(cap, push_cap), run_time=0.3)
        cue(self, "motors", sim_from=KICK_T - 0.4, sim_to=KICK_T + 0.6, run_time=1.0)
        cue(self, "thump", dt=0.4)
        self.play(t.animate.set_value(KICK_T + 0.6), run_time=1.0, rate_func=linear)

        drift_cap = caption("PID saves the stick...\nbut the cart runs away.").move_to(cap_area)
        cue(self, "pop")
        self.play(Transform(cap, drift_cap), run_time=0.3)
        cue(self, "motors", sim_from=KICK_T + 0.6, sim_to=T_SIM, run_time=T_SIM - KICK_T - 0.6)
        self.play(t.animate.set_value(T_SIM), run_time=T_SIM - KICK_T - 0.6, rate_func=linear)
        self.wait(0.6)

        why = caption("LQR also feels where the cart is\nand how fast it moves, so it comes home.",
                      SMALL, GOOD).move_to(cap_area)
        cue(self, "chime")
        self.play(Transform(cap, why), run_time=0.4)
        self.wait(2.5)

        outro = VGroup(
            Text("PID: 1 signal in", font_size=BODY, color=ACCENT),
            Text("LQR: position, velocity, angle, spin", font_size=BODY, color=GOOD),
        ).arrange(DOWN, buff=0.15).move_to(cap_area)
        cue(self, "whoosh")
        self.play(FadeOut(cap), FadeIn(outro), run_time=0.5)
        self.wait(2.5)
        save_cues(pathlib.Path(__file__).resolve().parents[1] / "renders" / "inverted_pendulum_pid_vs_lqr_cues.json")
