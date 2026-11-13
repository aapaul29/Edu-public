# STEM Animations

Source code and final renders for my short STEM explainer videos: the math, physics and engineering ideas I find beautiful, animated in Python.

Saw one of the videos and want to see how it was made, pause on a frame, or change the parameters and render your own version? Everything you need is here.

## Videos

| Video | Topic | Made with | Watch | Code |
|---|---|---|---|---|
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
│   │   └── taylor-series/
│   └── robotics-and-control/
│       └── inverted-pendulum-pid-vs-lqr/
├── common/style.py        # shared colors, fonts and the vertical 9:16 setup
└── requirements.txt
```

Each video folder looks the same:

```
<video>/
├── README.md     # what the video shows and how it was built
├── scenes/       # the Python code (Manim scenes, simulations)
└── renders/      # the finished video as mp4
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

## Tools

- [Manim Community](https://www.manim.community/) for the animations
- [NumPy](https://numpy.org/) and [SciPy](https://scipy.org/) for the simulations and control design
- [MuJoCo](https://mujoco.org/) for the upcoming 3D robot videos

## License

The code is under the [MIT License](LICENSE): use it, change it, learn from it. The rendered videos are mine; if you repost one, please credit and link back.
