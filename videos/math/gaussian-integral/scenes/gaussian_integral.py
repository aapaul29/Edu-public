"""Extracted from gaussian_integral.ipynb — render with:
    manim -pqm gaussian_integral.py GaussianIntegralScene
"""
from manim import *

class GaussianIntegralScene(Scene):
    def construct(self):
        # Scene 1: Introduction
        self.scene_1()
        self.wait(2)
        self.clear()

        # Scene 2: The clever trick
        self.scene_2()
        self.wait(2)
        self.clear()

        # Scene 3: Cylindrical coordinates
        self.scene_3()
        self.wait(2)
        self.clear()

        # Scene 4: Surface element theory
        self.scene_4()
        self.wait(2)
        self.clear()

        # Scene 5: Jacobian calculation
        self.scene_5()
        self.wait(2)
        self.clear()

        # Scene 6: Setting up the integral
        self.scene_6()
        self.wait(2)
        self.clear()

        # Scene 7: Evaluating chi
        self.scene_7()
        self.wait(2)
        self.clear()

        # Scene 8: Final result
        self.scene_8()
        self.wait(2)
        self.clear()

        # Scene 9: Applications
        self.scene_9()
        self.wait(3)

    def scene_1(self):
        title = Text("Solving the Gaussian Integral", font_size=36, color=GREEN).to_edge(UP)

        integral = MathTex(
            r"I = \int_{-\infty}^{\infty} e^{-x^2} dx",
            font_size=48,
            color=YELLOW
        ).move_to(ORIGIN)

          # Create axes and graph
        axes = Axes(
          x_range=[-4, 4, 1],
          y_range=[0, 1.2, 0.2],
          axis_config={"color": BLUE},
          x_axis_config={
            "numbers_to_include": np.arange(-4, 5, 2),
          },
          y_axis_config={
            "numbers_to_include": np.arange(0, 1.2, 0.2),
          }
          ).scale(0.9).shift(DOWN*0.5)

        graph = axes.plot(
          lambda x: np.exp(-x**2),
          color=RED,
          x_range=[-4, 4]
        )

        # Area under the curve
        area = axes.get_area(
        graph,
        x_range=(-4, 4),
        color=[BLUE_D, BLUE_E],
        opacity=0.5
        )

        # Animation sequence
        self.play(Write(title))
        self.play(Write(integral))
        self.wait(1)

        # Fade out title and move integral up
        self.play(
        FadeOut(title),
        integral.animate.to_edge(UP)
        )

        # Draw axes and graph
        self.play(
        Create(axes),
        run_time=1.5
        )
        self.play(
        Create(graph),
        run_time=2
        )

        # Fill area under curve
        self.play(
        FadeIn(area),
        run_time=2
        )


    def scene_2(self):
        title = Text("A clever trick is to use surface integrals", font_size=32, color=GREEN).to_edge(UP)

        equations = VGroup(
            MathTex(r"I_1 = I = \int_{-\infty}^{\infty} e^{-x^2} dx", color=YELLOW),
            MathTex(r"I_2 = I = \int_{-\infty}^{\infty} e^{-y^2} dy", color=YELLOW),
            MathTex(r"I_1 I_2 = I^2 = \int_{-\infty}^{\infty} e^{-x^2} dx \cdot \int_{-\infty}^{\infty} e^{-y^2} dy", color=ORANGE),
            MathTex(r"I^2 = \int_{-\infty}^{\infty} \int_{-\infty}^{\infty} e^{-x^2} \cdot e^{-y^2} dx dy", color=ORANGE),
            MathTex(r"I^2 = \iint_{\mathbb{R}^2} e^{-(x^2 + y^2)} \,dA", color=RED)
        ).arrange(DOWN, buff=0.5).scale(0.8).next_to(title, DOWN, buff=0.5)

        self.play(Write(title))

        for eq in equations:
            self.play(Write(eq))
            self.wait(0.5)

    def scene_3(self):
        title = Text("Since in cylindrical coordinates,", font_size=32, color=GREEN).to_edge(UP)

        coord_eq = MathTex(r"x^2 + y^2 = \rho^2", color=PURPLE).next_to(title, DOWN, buff=0.5)
        explanation = Text("it makes sense to change to a cylindrical base", font_size=28, color=GREEN).next_to(coord_eq, DOWN)

        integral_eq = MathTex(r"I^2 = \iint_{\mathbb{R}^2} e^{-\rho^2} dA", color=RED).next_to(explanation, DOWN, buff=0.5)

        warning = Text("Careful! The surface element in a cylindrical base is not just", font_size=24, color=ORANGE).next_to(integral_eq, DOWN, buff=0.5)
        wrong_da = MathTex(r"dA = d\rho d\varphi", color=RED).next_to(warning, DOWN)

        self.play(Write(title))
        self.play(Write(coord_eq))
        self.play(Write(explanation))
        self.play(Write(integral_eq))
        self.play(Write(warning))
        self.play(Write(wrong_da))

    def scene_4(self):
        title = Text("The surface element can be determined as follows:", font_size=32, color=GREEN).to_edge(UP)

        da_formula = MathTex(r"dA = |\det(J)| d\rho d\varphi", color=YELLOW).next_to(title, DOWN, buff=0.5)

        jacobian_text = Text("with J being the Jacobian Matrix:", font_size=28, color=GREEN).next_to(da_formula, DOWN, buff=0.5)

        jacobian = MathTex(
            r"J = \begin{pmatrix} \frac{\partial x}{\partial \rho} & \frac{\partial x}{\partial \varphi} \\ \frac{\partial y}{\partial \rho} & \frac{\partial y}{\partial \varphi} \end{pmatrix}",
            color=PURPLE
        ).next_to(jacobian_text, DOWN, buff=0.5)

        self.play(Write(title))
        self.play(Write(da_formula))
        self.play(Write(jacobian_text))
        self.play(Write(jacobian))

    def scene_5(self):
        title = Text("With the coordinate transformation being:", font_size=32, color=GREEN).to_edge(UP)

        transformations = VGroup(
            MathTex(r"x(\rho, \varphi) = \rho \cos(\varphi)", color=YELLOW),
            MathTex(r"y(\rho, \varphi) = \rho \sin(\varphi)", color=YELLOW)
        ).arrange(DOWN).next_to(title, DOWN, buff=0.5)

        jacobian_text = Text("The Jacobian results in:", font_size=28, color=GREEN).next_to(transformations, DOWN, buff=0.5)

        jacobian_calc = VGroup(
            MathTex(r"J = \begin{pmatrix} \cos(\varphi) & -\rho \sin(\varphi) \\ \sin(\varphi) & \rho \cos(\varphi) \end{pmatrix}", color=PURPLE),
            MathTex(r"\Rightarrow |\det(J)| = |-\rho \cos^2(\varphi) - \rho \sin^2(\varphi)|", color=ORANGE),
            MathTex(r"= \rho", color=ORANGE),
            MathTex(r"\Rightarrow dA = \rho d\rho d\varphi", color=RED)
        ).arrange(DOWN, buff=0.3).next_to(jacobian_text, DOWN, buff=0.5).scale(0.9)

        self.play(Write(title))
        self.play(Write(transformations))
        self.play(Write(jacobian_text))

        for calc in jacobian_calc:
            self.play(Write(calc))
            self.wait(0.5)

    def scene_6(self):
        equations = VGroup(
            MathTex(r"\Rightarrow I^2 = \int_0^{2\pi} \int_0^{\infty} \rho e^{-\rho^2} d\rho d\varphi", color=YELLOW),
            MathTex(r"I^2 = \int_0^{2\pi} d\varphi \cdot \int_0^{\infty} \rho e^{-\rho^2} d\rho", color=ORANGE),
            MathTex(r"I^2 = 2\pi \cdot \chi \text{ with } \chi = \int_0^{\infty} \rho e^{-\rho^2} d\rho", color=RED)
        ).arrange(DOWN, buff=0.7).move_to(ORIGIN).scale(0.9)

        for eq in equations:
            self.play(Write(eq))
            self.wait(0.5)

    def scene_7(self):
        title = Text("Evaluate χ:", font_size=36, color=GREEN).to_edge(UP)

        chi_def = MathTex(r"\chi = \int_0^{\infty} \rho e^{-\rho^2} d\rho", color=YELLOW).next_to(title, DOWN, buff=0.5)

        substitution = VGroup(
            Text("Sub:", font_size=28, color=GREEN),
            MathTex(r"u = \rho^2 \Rightarrow \frac{du}{d\rho} = 2\rho \Leftrightarrow d\rho = \frac{du}{2\rho}", color=PURPLE)
        ).arrange(RIGHT).next_to(chi_def, DOWN, buff=0.5)

        calculation = VGroup(
            MathTex(r"\chi = \int_0^{\infty} \rho e^{-u} \frac{du}{2\rho}", color=ORANGE),
            MathTex(r"= \frac{1}{2} \int_0^{\infty} e^{-u} du = -\frac{1}{2} \lim_{u \to \infty} [e^{-u}]_0^{\infty} = \frac{1}{2}", color=ORANGE),
        ).arrange(DOWN, buff=0.3).next_to(substitution, DOWN, buff=0.5).scale(0.9)

        self.play(Write(title))
        self.play(Write(chi_def))
        self.play(Write(substitution))

        for calc in calculation:
            self.play(Write(calc))
            self.wait(0.5)

    def scene_8(self):
        final_result = VGroup(
            MathTex(r"I^2 = \pi", color=YELLOW, font_size=48),
            MathTex(r"\Leftrightarrow I = \sqrt{\pi}", color=RED, font_size=48)
        ).arrange(DOWN, buff=1).move_to(ORIGIN)

        ##Sorrounding box
        # Create a surrounding rectangle
        box = SurroundingRectangle(
        final_result[1],
        color=YELLOW,
        buff=0.5,  # Padding around the text
        corner_radius=0.2,  # Optional rounded corners
        stroke_width=2  # Line thickness
    )


        self.play(Write(final_result[0]))
        self.play(Transform(final_result[0], final_result[1]))
        self.play(Write(final_result[1]))
        self.play(Create(box))
        self.wait(2.5)

    def scene_9(self):
        title = Text("Applications of the Gaussian Integral", font_size=32, color=GREEN).to_edge(UP)

        applications = VGroup(
            Text("• Probability & Statistics: Normalizes Gaussian distributions in the Central", font_size=20, color=YELLOW),
            Text("  Limit Theorem and hypothesis testing.", font_size=20, color=YELLOW),
            MathTex(r"\varphi(x) = \frac{1}{\sqrt{2\pi}\sigma} e^{-\frac{1}{2}\left(\frac{x-\mu}{\sigma}\right)^2}", font_size=35, color=ORANGE),
            Text("• Quantum Mechanics: Solves Schrödinger's equation and Feynman path", font_size=20, color=PURPLE),
            Text("  integrals for particle behavior.", font_size=20, color=PURPLE),
            Text("• Thermodynamics: Describes Maxwell-Boltzmann gas molecule speeds", font_size=20, color=BLUE),
            Text("  and partition functions.", font_size=20, color=BLUE),
            Text("• Signal Processing: Fourier transforms Gaussian signals for radar, noise", font_size=20, color=GREEN),
            Text("  filtering, and communications.", font_size=20, color=GREEN),
            Text("• Machine Learning: Trains Gaussian processes, Kalman filters, and", font_size=20, color=RED),
            Text("  expectation-maximization algorithms.", font_size=20, color=RED),
            Text("• Mathematics: Solves heat equations, generalizes to higher dimensions,", font_size=20, color=PINK),
            Text("  and approximates integrals.", font_size=20, color=PINK),
            Text("• Finance: Prices options via Black-Scholes models and assesses risk in", font_size=20, color=TEAL),
            Text("  Value-at-Risk (VaR).", font_size=20, color=TEAL),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(title, DOWN, buff=0.5).scale(0.8)

        conclusion = Text(
            "From quantum particles to stock markets—Gauss's integral shapes our\nunderstanding of randomness, motion, and uncertainty!",
            font_size=24,
            color=GOLD
        )

        self.play(Write(title))
        self.play(FadeIn(applications))
        self.wait(1)
        self.play(FadeOut(title, applications))
        self.play(Write(conclusion))
        self.wait(1)
        self.clear()
