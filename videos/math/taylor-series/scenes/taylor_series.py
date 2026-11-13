"""Extracted from taylor_series.ipynb — render with:
    manim -pqm taylor_series.py TaylorExpansion
"""
from manim import *
import numpy as np
from math import factorial

class TaylorExpansion(Scene):
    def construct(self):
        # Title
        title = Tex(r"Taylor Series Expansion of $e^x$", color=BLUE)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Initial equation and question
        equation = MathTex(
            r"e^x = \sum_{n=0}^{\infty} \frac{x^n}{n!}",
            color=YELLOW
        )

        question = Tex("But why?")
        question.next_to(equation, RIGHT, buff=0.5)
        self.play(Write(equation))
        self.play(Write(question))
        self.wait(2)
        self.play(FadeOut(equation), FadeOut(question))
        self.wait(1)

        # Taylor Serie Formula and explanation
        taylor_series = MathTex(
          r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(x_0)}{n!}(x - x_0)^n",
          color=BLUE
        )
        text = Tex("Taylor Series Formula:")
        taylor_series.next_to(text, DOWN, buff=0.5)
        self.play(Write(text), Write(taylor_series))
        self.wait(2)
        self.play(FadeOut(taylor_series), FadeOut(text))

        explanation = VGroup(
            Tex("Taylor series approximates a function around "),
            Tex("a x-value using its derivatives (here x=0)."),
            Tex("For $e^x$, all derivatives are $e^x$,"),
            Tex("and $e^0 = 1$, so:"),
        ).arrange(DOWN, aligned_edge=LEFT).scale(0.8)

        self.play(Write(explanation))
        self.wait(4)
        self.play(FadeOut(explanation))
        self.wait(1)

        # Show derivatives
        derivatives = VGroup(
            MathTex(r"f(x) = e^x \Rightarrow f(0) = 1", color=GREEN),
            MathTex(r"f'(x) = e^x \Rightarrow f'(0) = 1", color=GREEN),
            MathTex(r"f''(x) = e^x \Rightarrow f''(0) = 1", color=GREEN),
            MathTex(r"\vdots"),
            MathTex(r"f^{(n)}(x) = e^x \Rightarrow f^{(n)}(0) = 1", color=GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).scale(0.8)

        self.play(Write(derivatives))
        self.wait(3)
        self.play(FadeOut(derivatives))
        self.wait(1)

        # Apply to Taylor Series to e^x
        applied = MathTex(
        r"e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots + \frac{x^n}{n!} = \sum_{n=0}^{\infty} \frac{x^n}{n!}",
        color=YELLOW
    ).scale(0.9)
        self.play(Write(applied))
        self.wait(3)

        # Prepare for graph
        self.play(FadeOut(title), FadeOut(applied))

        # Graph setup
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-1, 8, 1],
            axis_config={"color": BLUE},
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")
        graph_group = VGroup(axes, axes_labels).scale(0.7)

        # Original e^x graph
        exp_graph = axes.plot(
            np.exp,
            color=RED,
        )
        exp_label = axes.get_graph_label(
            exp_graph, label="y = e^x", x_val=2, direction=LEFT
        )

        self.play(Create(axes), Write(axes_labels))
        self.play(Create(exp_graph), Write(exp_label))
        self.wait(2)
        self.play(FadeOut(exp_label))

        # Taylor series approximations
        colors = [GREEN, YELLOW, PURPLE, ORANGE, PINK]
        approx_graphs = []
        approx_labels = []

        def taylor_approx(x, degree):
            return sum([x**k / factorial(k) for k in range(degree+1)])

        for n in range(1, 6):
            # Create graph
            graph = axes.plot(
                lambda x: taylor_approx(x, n),
                color=colors[n-1],
            )
            # Position label on the left side, middle vertically
            label = Tex(f"Degree {n} approximation", color=colors[n-1]).scale(0.8)
            label.to_edge(UL) # Place left of y-axis



            approx_graphs.append(graph)
            approx_labels.append(label)

            # Animate creation
            self.play(
                Create(graph),
                Write(label),
                run_time=1
            )
            self.wait(1)
            self.play(FadeOut(label))
            self.play(FadeOut(graph))
            self.wait(1)

        # Clean up
        self.play(
            FadeOut(exp_graph),
            FadeOut(axes),
            FadeOut(axes_labels),
        )
        self.wait(2)


        # Show convergence
        convergence_text = Tex("As more terms are added, the approximation",
                              "converges to $e^x$ over a wider range.",
                              color=BLUE).scale(0.7)
        self.play(Write(convergence_text))
        self.wait(3)
        self.play(FadeOut(convergence_text))


        # Conclusion
        conclusion = Tex("This is why $e^x$ equals to this fascinating sum!",
                        color=GREEN).scale(0.8)
        self.play(Write(conclusion))
        self.wait(3)
        self.play(conclusion.animate.to_edge(UP))
        self.wait(1)

        # Highlight the exact match
        self.play(Write(equation))
        highlight_rect = SurroundingRectangle(equation, color=YELLOW, buff=0.2)
        self.play(Create(highlight_rect))
        self.wait(2)


        # Final Text
        final_text = Tex("The Taylor series expansion perfectly represents $e^x$!",
                        color=YELLOW).scale(0.8)
        final_text.next_to(equation, DOWN, buff=0.7)
        self.play(Write(final_text))
        self.wait(3)
        self.play(FadeOut(conclusion), FadeOut(final_text), FadeOut(equation), FadeOut(highlight_rect))
