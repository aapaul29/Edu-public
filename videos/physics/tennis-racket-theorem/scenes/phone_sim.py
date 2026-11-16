"""Tennis racket theorem: a phone spinning freely (no gravity) in MuJoCo, about each of its three axes.

Run from the repo root to simulate, sanity-check and render the frames the Manim scene uses:
    MUJOCO_GL=egl python videos/physics/tennis-racket-theorem/scenes/phone_sim.py
Frames go to videos/physics/tennis-racket-theorem/media/frames/<run>/0000.png (git-ignored).

Importing this module only simulates (fast); it does not render.

Body frame of the phone: x = long axis, y = width axis, z = through the screen.
    I_x (long)  <  I_y (middle)  <  I_z (screen)
Spinning about x or z is stable; spinning about y (end over end) is not: it flips.
"""
import pathlib

import mujoco
import numpy as np
from scipy.integrate import solve_ivp

HERE = pathlib.Path(__file__).resolve().parent
FRAMES = HERE.parent / "media" / "frames"

# ---------------------------------------------------------------- phone
MASS = 0.19                               # kg
LEN, WID, THK = 0.147, 0.071, 0.008       # m
I_LONG = MASS * (WID**2 + THK**2) / 12
I_MID = MASS * (LEN**2 + THK**2) / 12
I_SCREEN = MASS * (LEN**2 + WID**2) / 12
INERTIA = np.array([I_LONG, I_MID, I_SCREEN])

OMEGA = 2 * np.pi * 1.0                   # main spin: 1 revolution per second
EPS = 0.004                               # tiny wobble on the other two axes (a real throw is never perfect)
FPS = 30
DT = 0.0005


def _rgb(h):
    h = h.lstrip("#")
    return " ".join(f"{int(h[i:i + 2], 16) / 255:.3f}" for i in (0, 2, 4))


BG, BLUE, ORANGE, GRAY = _rgb("#0E1116"), _rgb("#4FC3F7"), _rgb("#FFB74D"), _rgb("#5A6270")
ROD, ROD_R, ROD_RGB = 0.095, 0.0011, _rgb("#E8EAED")

XML = f"""
<mujoco model="phone">
  <option timestep="{DT}" gravity="0 0 0" integrator="RK4"/>
  <visual>
    <global offwidth="1440" offheight="1440"/>
    <quality offsamples="8"/>
    <headlight ambient=".35 .35 .35" diffuse=".55 .55 .55" specular=".25 .25 .25"/>
    <map znear="0.01"/>
  </visual>
  <asset>
    <texture name="sky" type="skybox" builtin="flat" rgb1="{BG}" rgb2="{BG}" width="16" height="16"/>
  </asset>
  <worldbody>
    <light directional="true" pos="0.3 -0.5 1" dir="-0.3 0.5 -1" diffuse=".5 .5 .5" specular=".3 .3 .3"/>
    <!-- spin-axis rods (world-fixed, visual only); made visible per run -->
    <geom name="rod_x" type="capsule" size="{ROD_R}" fromto="-{ROD} 0 0 {ROD} 0 0" rgba="{ROD_RGB} 0"
          contype="0" conaffinity="0"/>
    <geom name="rod_y" type="capsule" size="{ROD_R}" fromto="0 -{ROD} 0 0 {ROD} 0" rgba="{ROD_RGB} 0"
          contype="0" conaffinity="0"/>
    <geom name="rod_z" type="capsule" size="{ROD_R}" fromto="0 0 -{ROD} 0 0 {ROD}" rgba="{ROD_RGB} 0"
          contype="0" conaffinity="0"/>
    <body name="phone">
      <freejoint/>
      <inertial pos="0 0 0" mass="{MASS}" diaginertia="{I_LONG} {I_MID} {I_SCREEN}"/>
      <geom type="box" size="{LEN / 2} {WID / 2} {THK / 2}" rgba="{GRAY} 1" contype="0" conaffinity="0"/>
      <geom type="box" size="{LEN / 2 - 0.004} {WID / 2 - 0.003} 0.0006" pos="0 0 {THK / 2}"
            rgba="{BLUE} 1" contype="0" conaffinity="0"/>
      <geom type="box" size="{LEN / 2 - 0.003} {WID / 2 - 0.003} 0.0006" pos="0 0 {-THK / 2}"
            rgba="{ORANGE} 1" contype="0" conaffinity="0"/>
      <geom type="cylinder" size="0.009 0.0015" pos="{LEN / 2 - 0.018} {WID / 2 - 0.016} {-THK / 2 - 0.0015}"
            rgba=".15 .16 .19 1" contype="0" conaffinity="0"/>
    </body>
  </worldbody>
</mujoco>
"""


def _quat_from_axes(x, y, z):
    """Quaternion of the rotation whose columns are the body axes expressed in world coordinates."""
    q = np.zeros(4)
    mujoco.mju_mat2Quat(q, np.column_stack([x, y, z]).ravel())
    return q


X, Y, Z = np.eye(3)
# Each run: (orientation: body axes in world, body angular velocity, length [s])
RUNS_SPEC = {
    # long axis horizontal on screen, screen facing the camera (camera sits on -y)
    "long": (_quat_from_axes(X, Z, -Y), OMEGA * np.array([1, EPS, EPS]), 6.0),
    # spin like a record facing the camera
    "screen": (_quat_from_axes(X, Z, -Y), OMEGA * np.array([EPS, EPS, 1]), 6.0),
    # end over end: width axis horizontal, long axis vertical, screen facing the camera
    "mid": (_quat_from_axes(-Z, X, -Y), OMEGA * np.array([EPS, 1, EPS]), 70.0),
}


def simulate(name):
    """Returns dict with t, quat (N,4), w_body (N,3) sampled at FPS, plus conservation checks."""
    quat0, w0, length = RUNS_SPEC[name]
    model = mujoco.MjModel.from_xml_string(XML)
    data = mujoco.MjData(model)
    data.qpos[3:7] = quat0
    data.qvel[3:6] = w0                 # free joint: angular velocity in the body frame
    mujoco.mj_forward(model, data)
    steps_per_frame = round(1 / (FPS * DT))
    n = int(length * FPS) + 1
    t, quat, w = np.zeros(n), np.zeros((n, 4)), np.zeros((n, 3))
    Lw, E = np.zeros((n, 3)), np.zeros(n)
    for i in range(n):
        t[i], quat[i], w[i] = data.time, data.qpos[3:7], data.qvel[3:6]
        R = data.xmat[1].reshape(3, 3)
        Lw[i] = R @ (INERTIA * w[i])
        E[i] = 0.5 * np.sum(INERTIA * w[i] ** 2)
        for _ in range(steps_per_frame):
            mujoco.mj_step(model, data)
    return dict(t=t, quat=quat, w=w, L=Lw, E=E, model=model)


def euler_reference(name, t):
    """Torque-free Euler equations integrated independently with SciPy."""
    _, w0, length = RUNS_SPEC[name]
    I1, I2, I3 = INERTIA

    def rhs(_, w):
        return [(I2 - I3) / I1 * w[1] * w[2], (I3 - I1) / I2 * w[2] * w[0], (I1 - I2) / I3 * w[0] * w[1]]

    return solve_ivp(rhs, (0, t[-1] + 1e-9), w0, t_eval=t, rtol=1e-10, atol=1e-12).y.T


def flip_times(run):
    """Sim times where the middle-axis spin component changes sign (each one is a half-turn flip)."""
    wy, t = run["w"][:, 1], run["t"]
    idx = np.where(np.sign(wy[1:]) != np.sign(wy[:-1]))[0]
    return t[idx] + (t[idx + 1] - t[idx]) * wy[idx] / (wy[idx] - wy[idx + 1])


RUNS = {name: simulate(name) for name in RUNS_SPEC}
FLIPS = flip_times(RUNS["mid"])
GROWTH = OMEGA * np.sqrt((I_MID - I_LONG) * (I_SCREEN - I_MID) / (I_LONG * I_SCREEN))


def report():
    print(f"I_long = {I_LONG:.3e}  I_mid = {I_MID:.3e}  I_screen = {I_SCREEN:.3e}  kg m^2")
    print(f"linear growth rate of a wobble on the middle axis: {GROWTH:.2f} /s "
          f"(e-folding {1 / GROWTH:.2f} s)")
    for name, r in RUNS.items():
        ref = euler_reference(name, r["t"])
        dL = np.abs(r["L"] - r["L"][0]).max() / np.linalg.norm(r["L"][0])
        dE = np.abs(r["E"] - r["E"][0]).max() / r["E"][0]
        err = np.abs(r["w"] - ref).max() / OMEGA
        axis = {"long": 0, "screen": 2, "mid": 1}[name]
        others = np.delete(r["w"], axis, axis=1)
        print(f"[{name:6s}] |dL|/L = {dL:.1e}  |dE|/E = {dE:.1e}  max |w - Euler ref|/Omega = {err:.1e}  "
              f"main-axis spin min/max = {r['w'][:, axis].min() / OMEGA:+.3f}/{r['w'][:, axis].max() / OMEGA:+.3f}  "
              f"max wobble = {np.abs(others).max() / OMEGA:.3f}")
    print("middle-axis flips at t =", np.round(FLIPS, 2))
    print("time between flips:", np.round(np.diff(FLIPS), 2))


# ---------------------------------------------------------------- rendering
SIZE = 720                                   # saved frame size (rendered at 2x, then downsampled)
SPIN_ROD = {"long": "rod_x", "screen": "rod_y", "mid": "rod_x"}   # rod along the (world-fixed) spin axis
ROD_ALPHA = 0.55


def _camera():
    cam = mujoco.MjvCamera()
    cam.lookat[:] = 0
    cam.distance = 0.30
    cam.azimuth = 90 + 22                    # camera on -y, turned a little to show depth
    cam.elevation = -14
    return cam


def _project(cam, fovy, p):
    """World point -> pixel (x, y) in the saved SIZE x SIZE frame, for a free camera (lookat/azimuth/elevation)."""
    az, el = np.radians(cam.azimuth), np.radians(cam.elevation)
    fwd = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    pos = np.array(cam.lookat) - cam.distance * fwd
    right = np.cross(fwd, [0, 0, 1])
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = np.asarray(p) - pos
    z = d @ fwd
    k = 1 / np.tan(np.radians(fovy) / 2)
    return [float(SIZE / 2 * (1 + k * (d @ right) / z)), float(SIZE / 2 * (1 - k * (d @ up) / z))]


def render_all(still_only=False):
    import json
    import os
    os.environ.setdefault("MUJOCO_GL", "egl")
    from PIL import Image
    model = mujoco.MjModel.from_xml_string(XML)
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, 2 * SIZE, 2 * SIZE)
    cam = _camera()
    rods = {n: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_GEOM, n) for n in ("rod_x", "rod_y", "rod_z")}

    def shot(quat, visible_rods):
        for n, gid in rods.items():
            model.geom_rgba[gid, 3] = ROD_ALPHA if n in visible_rods else 0.0
        data.qpos[:3] = 0
        data.qpos[3:7] = quat
        mujoco.mj_forward(model, data)
        renderer.update_scene(data, camera=cam)
        return Image.fromarray(renderer.render()).resize((SIZE, SIZE), Image.LANCZOS)

    # still: the phone with its three axes, plus where the axis ends land in the image (for labels)
    FRAMES.mkdir(parents=True, exist_ok=True)
    q0 = RUNS_SPEC["mid"][0]
    shot(q0, rods).save(FRAMES / "axes.png")
    R0 = np.zeros(9)
    mujoco.mju_quat2Mat(R0, q0)
    R0 = R0.reshape(3, 3)
    tips = {name: [_project(cam, model.vis.global_.fovy, s * ROD * R0[:, k]) for s in (1, -1)]
            for k, name in enumerate(("long", "mid", "screen"))}
    (FRAMES / "axes.json").write_text(json.dumps(tips))
    print("axis tips (px):", tips)
    if still_only:
        return

    for name, r in RUNS.items():
        out = FRAMES / name
        out.mkdir(parents=True, exist_ok=True)
        for i, q in enumerate(r["quat"]):
            shot(q, {SPIN_ROD[name]}).save(out / f"{i:04d}.png")
        print(f"rendered {len(r['quat'])} frames -> {out}")


if __name__ == "__main__":
    import sys
    report()
    render_all(still_only="--still" in sys.argv)
