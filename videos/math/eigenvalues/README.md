# Eigenvalues & Eigenvectors

What a linear transformation does to vectors, why a few special vectors only get stretched, and how to find those eigenvalues and eigenvectors.

**Watch:** [`renders/eigenvalue_intro.mp4`](renders/eigenvalue_intro.mp4) · 16:9 · ~1:48

| Part | Scene class | Code |
|---|---|---|
| Intro | `EigenvalueNewIntroduction` | [`scenes/eigenvalue_intro.py`](scenes/eigenvalue_intro.py) |
| Deep dive (code only, not rendered yet) | `EigenvalueDeepDive` | [`scenes/eigenvalue_deep_dive.py`](scenes/eigenvalue_deep_dive.py) |

## Render

```bash
manim -qh videos/math/eigenvalues/scenes/eigenvalue_intro.py EigenvalueNewIntroduction
manim -qh videos/math/eigenvalues/scenes/eigenvalue_deep_dive.py EigenvalueDeepDive
```

Both scenes use Manim's OpenGL renderer (`config.renderer = "opengl"`). If that fails on your machine, change it to `"cairo"` at the top of the file.
