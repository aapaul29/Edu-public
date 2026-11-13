"""Extracted from eigenvalue_intro.ipynb — render with:
    manim -pqm eigenvalue_intro.py EigenvalueNewIntroduction
"""
##Improved animation
from manim import *
import numpy as np

# Configure for Google Colab rendering
config.media_width = "100%"
config.pixel_height = 720
config.pixel_width = 1280
config.frame_height = 8
config.frame_width = 14.2
config.renderer = "opengl"

class EigenvalueNewIntroduction(Scene):
    def construct(self):
        # Title and introduction
        title = Text("Understanding Eigenvalues & Eigenvectors", font_size=36)
        title.to_edge(UP)
        self.play(AddTextLetterByLetter(title))
        self.wait(1)
        self.play(FadeOut(title))

        # Basic definition
        definition = MathTex(r"A\vec{v} = \lambda\vec{v}")
        definition.scale(1.5)

        self.play(FadeIn(definition))
        self.wait(1)

        # Explanation text
        explanation = Text(
            "For a square matrix A, an eigenvector v is stretched\n"
            "or compressed by A without changing direction",
            font_size=28
        ).next_to(definition, DOWN, buff=0.75)
        self.play(Write(explanation))
        self.wait(2)

        # Clear for the next section
        self.play(
            FadeOut(definition),
            FadeOut(explanation)
        )
        self.wait(0.5)

        # Set up the coordinate system for visualization
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            axis_config={"include_tip": True},
        ).scale(0.8)

        # Add coordinate labels
        x_label = axes.get_x_axis_label("x", edge=RIGHT, direction=RIGHT)
        y_label = axes.get_y_axis_label("y", edge=UP, direction=UP)

        self.play(
            Create(axes),
            Write(x_label),
            Write(y_label)
        )
        self.wait(1)

        # Our example 2x2 matrix
        matrix_A = [[2, 1],
                   [1, 2]]
        matrix_tex = MathTex(r"A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}")
        matrix_tex.to_corner(UL, buff=0.5)
        self.play(Write(matrix_tex))
        self.wait(1)

        # Calculate eigenvalues and eigenvectors
        eigenvalues, eigenvectors = np.linalg.eig(matrix_A)

        # Create visual vectors
        vectors = []
        transformed_vectors = []
        vector_labels = []
        eigenvector_labels = []
        colors = [BLUE, GREEN]

        # Create some standard basis vectors
        standard_vectors = [
            Arrow(axes.c2p(0, 0), axes.c2p(1, 0), buff=0, color=RED),
            Arrow(axes.c2p(0, 0), axes.c2p(0, 1), buff=0, color=RED)
        ]
        standard_labels = [
            MathTex(r"\hat{\imath}").next_to(standard_vectors[0], DOWN),
            MathTex(r"\hat{\jmath}").next_to(standard_vectors[1], LEFT)
        ]

        # Show standard basis vectors
        for vector, label in zip(standard_vectors, standard_labels):
            self.play(Create(vector), Write(label))

        self.wait(1)

        # Show how the standard basis vectors transform
        transformed_standard = []
        for i, vec in enumerate([[1, 0], [0, 1]]):
            transformed = np.dot(matrix_A, vec)
            arrow = Arrow(
                axes.c2p(0, 0),
                axes.c2p(transformed[0], transformed[1]),
                buff=0,
                color=YELLOW
            )
            transformed_standard.append(arrow)

        # Explanation for transformation
        transform_text = Text("A transforms the standard basis vectors:", font_size=24)
        transform_text.to_corner(UR, buff=0.5)
        self.play(Write(transform_text))

        for i, (orig, trans) in enumerate(zip(standard_vectors, transformed_standard)):
            self.play(
                ReplacementTransform(orig.copy(), trans)
            )
            if i == 0:
                label = MathTex(r"A\hat{\imath}").next_to(trans, RIGHT)
            else:
                label = MathTex(r"A\hat{\jmath}").next_to(trans, UP)
            self.play(Write(label))
            self.wait(0.5)
            self.play(FadeOut(label))

        self.wait(1)

        # Clear the standard basis transformation
        self.play(
            *[FadeOut(obj) for obj in [*transformed_standard, *standard_vectors, *standard_labels, transform_text, *self.mobjects[-2:]]]  # Last two are the labels
        )
        self.wait(0.5)

        # Create eigenvectors
        for i in range(2):
            ev = eigenvectors[:, i]
            # Scale eigenvector for better visibility
            ev_scaled = ev * 2.5

            # Create vector
            vector = Arrow(
                axes.c2p(0, 0),
                axes.c2p(ev_scaled[0], ev_scaled[1]),
                buff=0,
                color=colors[i]
            )
            vectors.append(vector)

            # Transformed vector (eigenvector * eigenvalue)
            transformed = ev_scaled * eigenvalues[i]
            transformed_vector = Arrow(
                axes.c2p(0, 0),
                axes.c2p(transformed[0], transformed[1]),
                buff=0,
                color=colors[i],
                stroke_width=6
            )
            transformed_vectors.append(transformed_vector)

            # Labels
            vector_label = MathTex(f"\\vec{{v}}_{i+1}").next_to(vector.get_end(), UP if i == 0 else RIGHT)
            vector_label.set_color(colors[i])
            vector_labels.append(vector_label)

            eigenvector_label = MathTex(f"\\lambda_{i+1} = {eigenvalues[i]:.1f}")
            eigenvector_label.set_color(colors[i])
            eigenvector_labels.append(eigenvector_label)

        # Arrange eigenvalue labels
        VGroup(*eigenvector_labels).arrange(DOWN).to_corner(DL, buff=0.5)

        # Introduce eigenvectors
        ev_title = Text("Eigenvalues of A:", font_size=20).next_to(eigenvector_labels[0], UP, buff=0.3)
        self.play(Write(ev_title))

        # Show each eigenvector and its transformation
        for i in range(2):
            # Show eigenvector
            self.play(
                Create(vectors[i]),
                Write(vector_labels[i]),
                Write(eigenvector_labels[i])
            )
            self.wait(1)

            # Show transformation
            copy_vector = vectors[i].copy()
            eig_equation = MathTex(
                f"A\\vec{{v}}_{i+1} = \\lambda_{i+1}\\vec{{v}}_{i+1} = {eigenvalues[i]:.1f}\\vec{{v}}_{i+1}"
            ).set_color(colors[i])

            eig_equation.to_edge(UP)

            self.play(Write(eig_equation))
            self.play(ReplacementTransform(copy_vector, transformed_vectors[i]))
            self.wait(1)

            # Clear equation for next iteration
            if i == 0:
                self.play(FadeOut(eig_equation))
            if i == 1:
                self.play(FadeOut(eig_equation))
        self.wait(1)
        self.play(FadeOut(matrix_tex))

        # Show all eigenvectors as a basis
        self.play(
            *[FadeOut(obj) for obj in [*transformed_vectors, *vector_labels]]
        )
        self.wait(0.5)

        # Show how arbitrary vectors transform
        random_vector = np.array([1.5, 1])

        # Express as linear combination of eigenvectors
        coefficients = np.linalg.solve(eigenvectors, random_vector)

        # Original vector
        random_arrow = Arrow(
            axes.c2p(0, 0),
            axes.c2p(random_vector[0], random_vector[1]),
            buff=0,
            color=WHITE
        )
        random_label = MathTex(r"\vec{w}").next_to(random_arrow.get_end(), RIGHT)

        # Transformed vector
        transformed_random = np.dot(matrix_A, random_vector)
        transformed_arrow = Arrow(
            axes.c2p(0, 0),
            axes.c2p(transformed_random[0], transformed_random[1]),
            buff=0,
            color=YELLOW
        )
        transformed_label = MathTex(r"A\vec{w}").next_to(transformed_arrow.get_end(), RIGHT)

        # Show original vector
        self.play(
            Create(random_arrow),
            Write(random_label)
        )
        self.wait(1)

        # Decompose into eigenvectors
        components = []
        component_labels = []
        for i in range(2):
            component = coefficients[i] * eigenvectors[:, i]
            component_arrow = Arrow(
                axes.c2p(0, 0),
                axes.c2p(component[0], component[1]),
                buff=0,
                color=colors[i],
                stroke_opacity=0.7
            )
            components.append(component_arrow)

            component_label = MathTex(f"{coefficients[i]:.2f}\\vec{{v}}_{i+1}").set_color(colors[i])
            component_label.next_to(component_arrow.get_end(), UP if i == 0 else RIGHT)
            component_labels.append(component_label)

        # Show decomposition
        decomposition_text = Text("Any vector can be decomposed into eigenvectors:", font_size=24)
        decomposition_text.to_edge(UP)
        self.play(Write(decomposition_text))

        decomposition_eq = MathTex(
            r"\vec{w} = c_1\vec{v}_1 + c_2\vec{v}_2"
        ).to_edge(UR).shift(DOWN * 0.75)

        self.play(Write(decomposition_eq))
        self.wait(1.5)
        self.play(FadeOut(decomposition_eq))
        # Show components
        self.play(
            *[Create(comp) for comp in components],
            *[Write(label) for label in component_labels]
        )
        self.wait(1)

        # Show transformation
        self.play(ReplacementTransform(random_arrow.copy(), transformed_arrow))
        self.play(Write(transformed_label))
        self.wait(1)

        # Show transformation formula with eigenvalues
        transform_eq = MathTex(
            r"A\vec{w} = A(c_1\vec{v}_1 + c_2\vec{v}_2) = c_1\lambda_1\vec{v}_1 + c_2\lambda_2\vec{v}_2"
        ).to_edge(DOWN)
        #transform_eq.shift(LEFT*0.5)  # Adjust position

        self.play(Write(transform_eq))
        self.wait(1)

        # Transformed components
        transformed_components = []
        transformed_component_labels = []
        for i in range(2):
            t_component = coefficients[i] * eigenvalues[i] * eigenvectors[:, i]
            t_component_arrow = Arrow(
                axes.c2p(0, 0),
                axes.c2p(t_component[0], t_component[1]),
                buff=0,
                color=colors[i],
                stroke_opacity=0.7
            )
            transformed_components.append(t_component_arrow)

            t_component_label = MathTex(f"{coefficients[i]:.2f}\\lambda_{i+1}\\vec{{v}}_{i+1}").set_color(colors[i])
            t_component_label.next_to(t_component_arrow.get_end(), UP if i == 0 else RIGHT)
            transformed_component_labels.append(t_component_label)

        # Show transformed components
        self.play(
            *[FadeOut(comp) for comp in components],
            *[FadeOut(label) for label in component_labels],
            *[Create(comp) for comp in transformed_components],
            *[Write(label) for label in transformed_component_labels]
        )
        self.wait(2)

        # Clear the scene for the derivation
        self.play(
            *[FadeOut(obj) for obj in self.mobjects if obj != title]
        )
        self.wait(0.5)

        # Derivation of eigenvalue formula
        derivation_title = Text("Deriving the Eigenvalue Equation", font_size=36)
        derivation_title.to_edge(UP)
        self.play(Write(derivation_title))
        self.wait(1)

        # Start with the basic equation
        start_eq = MathTex(r"A\vec{v} = \lambda\vec{v}")
        start_eq.next_to(derivation_title, DOWN, buff=0.75)
        self.play(Write(start_eq))
        self.wait(1)

        # Rewrite the equation
        rewrite_eq = MathTex(r"A\vec{v} - \lambda\vec{v} = \vec{0}")
        rewrite_eq.next_to(start_eq, DOWN, buff=0.75)
        self.play(Write(rewrite_eq))
        self.wait(1)

        # Factor out v
        factored_eq = MathTex(r"(A - \lambda I)\vec{v} = \vec{0}")
        factored_eq.next_to(rewrite_eq, DOWN, buff=0.75)
        self.play(Write(factored_eq))
        self.wait(1)

        # Explain non-trivial solutions
        explanation_text = Text(
            "For non-trivial solutions (v ≠ 0), the matrix must be singular.",
            font_size=28
        )
        explanation_text.next_to(factored_eq, DOWN, buff=0.75)
        self.play(Write(explanation_text))
        self.wait(1)
        self.play(FadeOut(derivation_title, start_eq, rewrite_eq, factored_eq, explanation_text))
        # Determinant condition
        ex_text = Text("Criteria for matrex singularity: ", font_size=20)
        ex_text.to_edge(UP)
        det_eq = MathTex(r"\det(A - \lambda I) = 0")
        det_eq.next_to(ex_text, DOWN, buff=1.0)
        self.play(Write(ex_text))
        self.play(Write(det_eq))
        self.wait(1)
        self.play(FadeOut(ex_text))
        # Characteristic polynomial
        poly_text = Text("This is called the characteristic polynomial, p(λ)", font_size=20)
        poly_text.next_to(det_eq, DOWN, buff=1.0)
        self.play(Write(poly_text))
        self.wait(1.5)
        self.play(FadeOut(det_eq, poly_text))

        # Finding eigenvectors
        eigenvector_text = Text(
            "For each eigenvalue λ, eigenvectors are found by solving:",
            font_size=20
        )
        eigenvector_text.to_edge(UP)
        self.play(Write(eigenvector_text))
        self.wait(1)

        eigenvector_eq = MathTex(r"(A - \lambda I)\vec{v} = \vec{0}")
        eigenvector_eq.next_to(eigenvector_text, DOWN, buff=0.75)
        eig_eq_2 = MathTex(r"\vec{v} = ker(A - \lambda I)")
        eig_eq_2.next_to(eigenvector_eq, DOWN, buff=1.0)
        self.play(Write(eigenvector_eq))
        self.play(Write(eig_eq_2))
        self.wait(2)

        # Clear for conclusion
        #self.play(
            #*[FadeOut(obj) for obj in self.mobjects if obj != title]
        #)
        self.play(FadeOut(eigenvector_text, eigenvector_eq, eig_eq_2))
        self.wait(1.0)




        # Final message about eigenvalue importance
        conclusion_text = VGroup(
            Text("Eigenvalues and eigenvectors are fundamental to:", font_size=32),
            Text("- Understanding linear transformations", font_size=28),
            Text("- Solving differential equations", font_size=28),
            Text("- Quantum mechanics", font_size=28),
            Text("- Google's PageRank algorithm", font_size=28),
            Text("- Vibration analysis", font_size=28),
            Text("- Machine learning and data science", font_size=28),
            Text("- Many other mathematical applications", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)

        conclusion_text.scale(0.9).center()

        self.play(Write(conclusion_text))
        self.wait(3)

        self.play(
            FadeOut(conclusion_text)
        )
