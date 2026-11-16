# Why a spinning phone flips (tennis racket theorem)

Toss a phone end over end and it comes back flipped. The video spins the same phone about each of its three axes in a zero-gravity physics simulation. Around the **long axis** and the axis **through the screen** it spins steadily, but around the **middle axis** it flips over every 2.9 s, again and again. The axes with the smallest and the largest moment of inertia are stable; the one in between is not.

**Watch:** [`renders/tennis_racket_theorem.mp4`](renders/tennis_racket_theorem.mp4) · 1080×1920 · 1:45 · with voiceover

## The physics

- **Euler's equations** for torque-free rotation, linearized about a spin Ω around the middle axis, give ω̈₁ = Ω²(I₃−I₂)(I₂−I₁)/(I₁I₃)·ω₁. Both brackets are positive, so a tiny wobble grows like e^{λt}. For the other two axes the sign flips and the wobble just oscillates. For this phone λ = 4.9 s⁻¹, shown on a log plot against the simulation.
- **The angular-momentum sphere.** Energy and |L| are both conserved, so the spin direction moves along curves on a sphere: small loops around the stable axes, and a saddle through the middle axis. That's why the phone flips all the way over and back.

## Code

| File | What it does |
|---|---|
| [`scenes/phone_sim.py`](scenes/phone_sim.py) | [MuJoCo](https://mujoco.org/) simulation (free rigid body, RK4 at 2 kHz, no gravity), checks, and offscreen frame rendering |
| [`scenes/tennis_racket.py`](scenes/tennis_racket.py) | Manim scene `TennisRacket`: plays the frames and adds plots, equations and the sphere |
| [`scenes/voice.py`](scenes/voice.py) | voiceover lines; measures their length so the scene can time its pauses |
| [`scenes/make_audio.py`](scenes/make_audio.py) | mixes voice and sound effects onto the render |

## Render

```bash
MUJOCO_GL=egl python videos/physics/tennis-racket-theorem/scenes/phone_sim.py   # sim + checks + ~960 frames
manim -qh videos/physics/tennis-racket-theorem/scenes/tennis_racket.py TennisRacket
```

The voice is [Kokoro TTS](https://github.com/hexgrad/kokoro) (set `KOKORO_DIR`), mixed in by `make_audio.py`. The measured line lengths are already in `renders/tennis_racket_theorem_vo.json`, so the Manim scene renders without Kokoro installed.

## Model and checks

Phone 147 × 71 × 8 mm, 190 g (uniform box): I_long = 8.1, I_middle = 34.3, I_screen = 42.2 (×10⁻⁵ kg·m²). Spin 1 rev/s with a 0.4% wobble on the other two axes. Angular momentum and energy are conserved to 1e-9 and 1e-13, and MuJoCo matches an independent SciPy integration of Euler's equations to 5e-9. The stable spins never wobble more than 0.6%.
