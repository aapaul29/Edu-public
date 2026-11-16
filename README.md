# STEM Animations

Source code and final renders for my short STEM explainer videos: the math, physics and engineering ideas I find beautiful, animated in Python.

Saw one of the videos and want to see how it was made, pause on a frame, or change the parameters and render your own version? Everything you need is here.

## Videos

| Video | Topic | Made with | Watch | Code |
|---|---|---|---|---|
| **Why a spinning phone flips** (tennis racket theorem) | Physics | MuJoCo + Manim | [mp4](videos/physics/tennis-racket-theorem/renders/tennis_racket_theorem.mp4) | [folder](videos/physics/tennis-racket-theorem/) |
| **How PCA works: variance, eigenvectors and the SVD** | Math | Manim | [mp4](videos/math/pca-eigenvectors/renders/pca_eigenvectors.mp4) | [folder](videos/math/pca-eigenvectors/) |
| **How a drone holds its altitude: PID one term at a time** | Robotics & Control | Simulation + Manim | [mp4](videos/robotics-and-control/drone-pid-altitude/renders/drone_pid_altitude.mp4) | [folder](videos/robotics-and-control/drone-pid-altitude/) |
| **Balance a stick on a cart: PID vs LQR** | Robotics & Control | Simulation + Manim | [mp4](videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/renders/inverted_pendulum_pid_vs_lqr.mp4) | [folder](videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/) |
| **Eigenvalues & Eigenvectors** | Math | Manim | [mp4](videos/math/eigenvalues/renders/eigenvalue_intro.mp4) | [folder](videos/math/eigenvalues/) |
| **The Gaussian Integral** | Math | Manim | [mp4](videos/math/gaussian-integral/renders/gaussian_integral.mp4) | [folder](videos/math/gaussian-integral/) |
| **Taylor Series of eˣ** | Math | Manim | [mp4](videos/math/taylor-series/renders/taylor_series.mp4) | [folder](videos/math/taylor-series/) |

New videos land here as they come out.

## Repository layout

```
.
├── videos/
│   ├── math/
│   │   ├── eigenvalues/
│   │   ├── gaussian-integral/
│   │   ├── pca-eigenvectors/
│   │   └── taylor-series/
│   ├── physics/
│   │   └── tennis-racket-theorem/
│   └── robotics-and-control/
│       ├── drone-pid-altitude/
│       └── inverted-pendulum-pid-vs-lqr/
├── common/
│   ├── style.py           # shared colors, fonts and the vertical 9:16 setup
│   ├── sfx.py             # synthesized sound effects and audio mixing
│   └── phone_preview.py   # preview how a render looks inside the TikTok app
└── requirements.txt
```

Each video folder looks the same:

```
<video>/
├── README.md     # what the video shows and how it was built
├── scenes/       # the Python code (Manim scenes, simulations, audio mix)
└── renders/      # the finished video as mp4, plus timing data for the audio
```

## Render a video yourself

You need Python 3.10+, ffmpeg and a LaTeX distribution. The [Manim installation guide](https://docs.manim.community/en/stable/installation.html) walks through all three for Windows, macOS and Linux.

```bash
git clone https://github.com/aapaul29/Edu-public.git
cd Edu-public
pip install -r requirements.txt

# quick low-quality preview (opens when done)
manim -pql videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle

# full quality
manim -qh videos/robotics-and-control/inverted-pendulum-pid-vs-lqr/scenes/cartpole.py CartPoleBattle
```

Always run the commands from the repo root. Manim writes its output to `media/`, which git ignores. The scene class name for every video is listed in its README.

Newer videos are vertical (1080×1920) and use `common/style.py`. The older math videos are 16:9 and only need Manim itself.

Manim renders the picture without sound. Videos with audio have a `make_audio.py` next to the scene that adds the voiceover and sound effects afterwards; see each video's README.

## Tools

- [Manim Community](https://www.manim.community/) for the animations
- [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/) for the simulations and control design
- [MuJoCo](https://mujoco.org/) for 3D rigid-body simulations
- [Kokoro TTS](https://github.com/hexgrad/kokoro) for the AI voiceovers

## License

The code is under the [MIT License](LICENSE): use it, change it, learn from it. The rendered videos are mine; if you repost one, please credit and link back.
