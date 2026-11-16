# How a drone holds its altitude: PID one term at a time

A drone has to climb to 3 m and hover. The controller gets its terms one at a time with the same gains, and the altitude plot keeps every attempt for comparison:

- **P** pushes in proportion to the error. It bounces and hovers too low: at zero error it gives zero thrust, so it can't hold up the drone's weight.
- **PI** adds up the error over time. The sag disappears, but it overshoots and keeps wobbling.
- **PID** brakes when the error shrinks fast. It climbs smoothly to the target with no overshoot.

**Watch:** [`renders/drone_pid_altitude.mp4`](renders/drone_pid_altitude.mp4) · 1080×1920 · 46 s · with voiceover

## Code

| File | What it does |
|---|---|
| [`scenes/drone_pid.py`](scenes/drone_pid.py) | 1D altitude simulation (Euler at 1 kHz) and the Manim scene `DronePID` |
| [`scenes/make_audio.py`](scenes/make_audio.py) | mixes the voiceover and sound effects, including a rotor hum that follows the simulated thrust |

## Render

```bash
manim -qh videos/robotics-and-control/drone-pid-altitude/scenes/drone_pid.py DronePID
```

The voice is [Kokoro TTS](https://github.com/hexgrad/kokoro) (set `KOKORO_DIR`); `make_audio.py` adds it and the sound effects using `renders/drone_pid_altitude_cues.json`.

## Model

m = 1 kg, g = 9.81 m/s², linear drag 0.3 N·s/m, thrust 0–25 N, target 3 m. Gains Kp = 6, Ki = 1.5, Kd = 4, with no hover feedforward (that's why P alone sags to ~1.4 m). PI peaks at 3.95 m; PID reaches 2.93 m at 10 s without overshoot. Change the gains at the top of the file and see what happens.

Next step up: [balancing a stick on a cart, PID vs LQR](../inverted-pendulum-pid-vs-lqr/).
