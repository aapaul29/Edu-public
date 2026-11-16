"""How a drone holds its altitude: PID, one term at a time.

A 1 kg drone has to climb to 3 m and hover. The controller output is the total
thrust u. We add the terms one by one with the same gains:
  P   -> bounces and hovers too low (P alone can't supply hover thrust at zero error)
  PI  -> the integral fixes the sag but the drone overshoots and wobbles
  PID -> the derivative brakes it, smooth climb with no overshoot

Render from the repo root:
    manim -qh videos/robotics-and-control/drone-pid-altitude/scenes/drone_pid.py DronePID
"""
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4]))
from common.style import *  # noqa: E402,F403

vertical()

# ---------------------------------------------------------------- physics
MASS, G, DRAG = 1.0, 9.81, 0.3     # kg, m/s^2, linear air drag [N s/m]
UMAX, REF = 25.0, 3.0              # max thrust [N], target altitude [m]
T_SIM, DT = 10.0, 1 / 1000
KP, KI, KD = 6.0, 1.5, 4.0

# Pauses sized so the voiceover lines (see make_audio.py) fit their moments
INTRO_WAIT = 3.4
POST_WAIT = {"P": 2.8, "PI": 1.4, "PID": 1.4}
OUTRO_WAIT = 7.0


def simulate(kp, ki, kd):
    z = zd = integ = 0.0
    out = []
    for i in range(int(T_SIM / DT) + 1):
        e = REF - z
        integ += e * DT
        u = float(np.clip(kp * e + ki * integ - kd * zd, 0.0, UMAX))
        zdd = (u - MASS * G - DRAG * zd) / MASS
        if z <= 0 and zdd < 0:          # resting on the ground
            zdd, zd = 0.0, max(zd, 0.0)
        out.append((i * DT, z, u))
        zd += zdd * DT
        z = max(z + zd * DT, 0.0)
    return np.array(out)


RUNS = {"P": simulate(KP, 0, 0), "PI": simulate(KP, KI, 0), "PID": simulate(KP, KI, KD)}


def at(run, t):
    r = RUNS[run]
    return np.interp(t, r[:, 0], r[:, 1]), np.interp(t, r[:, 0], r[:, 2])


# ---------------------------------------------------------------- layout
GROUND_Y, M2U = -0.6, 0.85          # scene y of the ground, scene units per metre
DRONE_X = SAFE_CX                  # centered in the TikTok safe zone
COLORS = {"P": BAD, "PI": ACCENT_2, "PID": GOOD}


def alt_to_y(z):
    return GROUND_Y + M2U * z


def drone(z, u, color):
    y = alt_to_y(z) + 0.25
    body = RoundedRectangle(width=0.9, height=0.3, corner_radius=0.12,
                            fill_color=color, fill_opacity=1, stroke_width=0).move_to([DRONE_X, y, 0])
    arms = Line([DRONE_X - 0.85, y + 0.1, 0], [DRONE_X + 0.85, y + 0.1, 0], color=FG, stroke_width=5)
    rotors = VGroup(*[Ellipse(width=0.7, height=0.1, color=FG, stroke_width=3, fill_color=FG, fill_opacity=0.25)
                      .move_to([DRONE_X + dx, y + 0.2, 0]) for dx in (-0.85, 0.85)])
    # thrust arrows under the rotors, length proportional to thrust / weight
    length = 0.55 * u / (MASS * G)
    thrust = VGroup(*[Arrow([DRONE_X + dx, y - 0.05, 0], [DRONE_X + dx, y - 0.05 - max(length, 0.05), 0],
                            buff=0, color=ACCENT, stroke_width=6, max_tip_length_to_length_ratio=0.25)
                      for dx in (-0.85, 0.85)])
    return VGroup(thrust, arms, rotors, body)


class DronePID(Scene):
    def construct(self):
        title = Text("How a drone holds its altitude", font_size=TITLE, color=FG, weight=BOLD).move_to([SAFE_CX, TITLE_Y, 0])

        ground = Line([SAFE_LEFT, GROUND_Y, 0], [SAFE_RIGHT, GROUND_Y, 0], color=MUTED, stroke_width=3)
        target = DashedLine([SAFE_LEFT, alt_to_y(REF), 0], [SAFE_RIGHT, alt_to_y(REF), 0], color=FG, dash_length=0.15,
                            stroke_width=2)
        target_lab = Text("target: 3 m", font_size=SMALL, color=FG).next_to(target, UP, buff=0.1)
        target_lab.align_to([SAFE_LEFT + 0.1, 0, 0], LEFT)

        # altitude-vs-time plot
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 4, 1], x_length=5.0, y_length=2.2,
                    axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": True, "tick_size": 0.05},
                    ).move_to([SAFE_CX + 0.05, -3.35, 0])
        x_lab = Text("time [s]", font_size=SMALL, color=MUTED).next_to(axes.c2p(10, 0), UP + LEFT, buff=0.12)
        y_lab = Text("altitude [m]", font_size=SMALL, color=MUTED).next_to(axes.y_axis, UP, buff=0.1).align_to(axes.y_axis, LEFT)
        ref_line = DashedLine(axes.c2p(0, REF), axes.c2p(10, REF), color=FG, dash_length=0.1, stroke_width=1.5)

        self.add(title)
        parked = drone(0.0, 0.0, MUTED)
        cue(self, "whoosh")
        self.play(FadeIn(ground), FadeIn(target), FadeIn(target_lab), FadeIn(parked), run_time=0.8)
        cue(self, "tick")
        self.play(Create(axes), FadeIn(x_lab), FadeIn(y_lab), FadeIn(ref_line), run_time=1.0)
        self.wait(INTRO_WAIT)

        # formula that grows term by term
        f_p = MathTex(r"u", r"=", r"K_p\,e", color=FG).scale(0.95)
        f_pi = MathTex(r"u", r"=", r"K_p\,e", r"+K_i\!\int e\,dt", color=FG).scale(0.95)
        f_pid = MathTex(r"u", r"=", r"K_p\,e", r"+K_i\!\int e\,dt", r"+K_d\,\dot e", color=FG).scale(0.95)
        for f in (f_p, f_pi, f_pid):
            f.move_to([SAFE_CX, 4.55, 0])
        f_pi[3].set_color(ACCENT_2)
        f_pid[3].set_color(ACCENT_2)
        f_pid[4].set_color(GOOD)
        f_p[2].set_color(BAD)
        f_pi[2].set_color(BAD)
        f_pid[2].set_color(BAD)
        e_def = MathTex(r"e = \text{target} - \text{altitude}", color=MUTED).scale(0.6).move_to([SAFE_CX, 3.9, 0])

        notes = {
            "P": ("P: push harder the farther away you are", "...it bounces, and hovers too low"),
            "PI": ("I: add up the error over time", "...the sag is gone, but it overshoots"),
            "PID": ("D: brake when closing in fast", "...smooth, and right on target"),
        }
        formulas = {"P": f_p, "PI": f_pi, "PID": f_pid}
        cap_pos = [SAFE_CX, -1.05, 0]   # gap between the ground line and the plot

        prev_formula, prev_curve, prev_cap = None, None, None
        for run in ("P", "PI", "PID"):
            color = COLORS[run]
            t = ValueTracker(0)
            d = always_redraw(lambda run=run, t=t, color=color: drone(*at(run, t.get_value()), color))
            curve = always_redraw(lambda run=run, t=t, color=color: axes.plot(
                lambda s: at(run, s)[0], x_range=[0, max(t.get_value(), 0.02), 0.02], color=color, stroke_width=5))

            what, result = notes[run]
            cap = Text(what, font_size=SMALL, color=color).move_to(cap_pos)

            anims = [FadeIn(cap)]
            if prev_formula is None:
                anims += [Write(formulas[run]), FadeIn(e_def), FadeOut(parked)]
            else:
                anims += [TransformMatchingTex(prev_formula, formulas[run]), FadeOut(prev_cap)]
                prev_curve.clear_updaters()
                anims.append(prev_curve.animate.set_stroke(opacity=0.25))
            cue(self, "whoosh")
            cue(self, "pop")
            self.play(*anims, run_time=1.2)
            self.add(d, curve)
            cue(self, "hum", run=run, run_time=7.0, sim_time=T_SIM)
            self.play(t.animate.set_value(T_SIM), run_time=7.0, rate_func=linear)
            res = Text(result, font_size=SMALL, color=FG).move_to(cap.get_center() + DOWN * 0.45)
            cue(self, "chime" if run == "PID" else "wrong")
            self.play(FadeIn(res), run_time=0.4)
            self.wait(POST_WAIT[run])
            self.play(FadeOut(res), FadeOut(d), run_time=0.4)
            prev_formula, prev_curve, prev_cap = formulas[run], curve, cap

        prev_curve.clear_updaters()
        outro = VGroup(
            Text("P = present error", font_size=BODY, color=BAD),
            Text("I = past error", font_size=BODY, color=ACCENT_2),
            Text("D = where the error is heading", font_size=BODY, color=GOOD),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to([SAFE_CX, 0.7, 0])
        cue(self, "whoosh")
        self.play(FadeOut(prev_cap), FadeIn(outro, shift=UP * 0.2), run_time=0.8)
        self.wait(OUTRO_WAIT)
        save_cues(pathlib.Path(__file__).resolve().parents[1] / "renders" / "drone_pid_altitude_cues.json")
