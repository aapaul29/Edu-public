# How PCA works: variance, eigenvectors and the SVD

PCA on real handwritten digits: 1,797 scanned digits, each an 8×8 image with ink values from 0 to 16, so every image is a point in 64-dimensional space.

**Watch:** [`renders/pca_eigenvectors.mp4`](renders/pca_eigenvectors.mp4) · 1080×1920 · 1:48 · with voiceover

## What the video covers

1. **What PCA is for.** Most of the 64 numbers move together. PCA looks for new axes where a few numbers keep most of the variation.
2. **A 2D example.** Ink in a 2×2 patch at the top of the image vs a patch at the bottom of the same columns (correlation 0.78), centered on the mean.
3. **Spin a line.** Every image is projected onto a rotating line while a meter shows the variance it keeps. The best line keeps the most variance and, equivalently, leaves the smallest squared errors. That's PC 1 (89% of the variance here).
4. **Eigenvectors.** With the centered data matrix X, the covariance is Σ = XᵀX/n. PC 1 is its top eigenvector, and the eigenvalue λ₁ = 17.97 is exactly the variance the meter showed.
5. **SVD.** X = U S Vᵀ: Vᵀ rotates the cloud onto its principal axes, S says how far it stretches along each, U holds every image's new coordinates. Substituting gives XᵀX/n = V (S²/n) Vᵀ, so λᵢ = σᵢ²/n: 179.7²/1797 = 17.97.
6. **All 64 pixels.** The principal components are images themselves ("eigen-digits"). Rebuilding a 3 from k of them keeps 15% of the variance at k = 1, 54% at k = 5, 89% at k = 20. With just 2 numbers per image the ten digits form groups, although PCA never saw a label.

A sequel to [Eigenvalues & Eigenvectors](../eigenvalues/).

## Code

| File | What it does |
|---|---|
| [`scenes/pca.py`](scenes/pca.py) | Manim scene `PCAEigen`: all the math, computed from the data at render time |
| [`scenes/digits.csv`](scenes/digits.csv) | the dataset |
| [`scenes/make_audio.py`](scenes/make_audio.py) | mixes the AI voiceover and sound effects onto the render |

## Render

```bash
manim -qh videos/math/pca-eigenvectors/scenes/pca.py PCAEigen
```

This gives the silent video. The voice comes from [Kokoro TTS](https://github.com/hexgrad/kokoro) (set `KOKORO_DIR`) and the sound effects from `common/sfx.py`; `make_audio.py` puts them together using the timings in `renders/pca_eigenvectors_cues.json`.

## Data

"Optical Recognition of Handwritten Digits" by E. Alpaydin and C. Kaynak (UCI Machine Learning Repository, CC BY 4.0), in the 8×8 version that ships with scikit-learn. Statistics use all 1,797 images; the 2D plots draw a random 350 so the projections stay readable. All numbers use the 1/n convention, so λᵢ = σᵢ²/n exactly.
