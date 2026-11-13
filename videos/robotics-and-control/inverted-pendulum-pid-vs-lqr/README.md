# Balance a stick on a cart: PID vs LQR

Two carts get the same tilted pendulum and, a few seconds later, the same push. PID only watches the angle: it keeps the stick up, but its cart drifts about 7 m away. LQR uses all four states (cart position, cart velocity, angle, angular velocity), so it catches the stick *and* brings the cart back to the center.

**Watch:** [`renders/inverted_pendulum_pid_vs_lqr.mp4`](renders/inverted_pendulum_pid_vs_lqr.mp4) · 1080×1920 · ~22 s

## How it's made

1. The full nonlinear cart-pole equations are integrated with RK4 (dt = 1/600 s) for both controllers.
2. The LQR gain comes from solving the continuous algebraic Riccati equation on the linearized model (`scipy.linalg.solve_continuous_are`).
3. The precomputed trajectories are played back in Manim with a `ValueTracker`.

## Parameters

| | |
|---|---|
| Cart / bob mass | 1 kg / 0.2 kg |
| Rod | 0.6 m, massless |
| Force limit | ±25 N |
| Initial tilt | 0.3 rad (~17°) |
| Push | +1.2 rad/s on the pole at t = 6 s |
| LQR weights | Q = diag(10, 1, 100, 1), R = 0.1 |
| PID gains (on the angle) | Kp = 60, Kd = 12, Ki = 20 |

All of them sit at the top of [`scenes/cartpole.py`](scenes/cartpole.py). Try a bigger push or a weaker motor and see which controller gives up first.

## Render

```bash
manim -qh videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle
```
