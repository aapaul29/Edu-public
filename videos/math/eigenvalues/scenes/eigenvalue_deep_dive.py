"""Extracted from eigenvalue_deep_dive.ipynb — render with:
    manim -pqm eigenvalue_deep_dive.py EigenvalueDeepDive
"""
from manim import *
import numpy as np

#Configure for Google Colab rendering (or local rendering)
config.media_width = "100%"
config.pixel_height = 720
config.pixel_width = 1280
config.frame_height = 8.0 # Ensure float
config.frame_width = 14.22 # Ensure float, often 16/9 * frame_height
config.renderer = "opengl" # or "cairo"

class EigenvalueDeepDive(Scene):
    def construct(self):
        # --- SCENE 1: The Dance of Vectors ---
        title = Text("Eigenvalues & Eigenvectors: The Transformation's Secrets", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Introduce Linear Transformation
        intro_text = Text(
            "Linear transformations change vectors and space.", font_size=28
        ).next_to(title, DOWN, buff=0.5)
        self.play(Write(intro_text))
        self.wait(1)

        # Setup NumberPlane
        plane = NumberPlane(
            x_range=[-5, 5, 1], y_range=[-4, 4, 1],
            x_length=10, y_length=7,
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 2,
                "stroke_opacity": 0.5
            }
        ).add_coordinates()
        plane.shift(DOWN*0.5)

        self.play(FadeOut(intro_text), Create(plane))
        self.wait(0.5)

        matrix_A_val = np.array([[1, 1],
                                 [0.5, 2]]) # A slightly more illustrative matrix for general transform

        matrix_A_tex_intro = MathTex(r"A = \begin{bmatrix} 1 & 1 \\ 0.5 & 2 \end{bmatrix}").to_corner(UL)
        self.play(Write(matrix_A_tex_intro))

        # Show some random vectors transforming
        vec1_orig = Vector([1,1], color=PINK)
        vec2_orig = Vector([-2,0.5], color=ORANGE)
        vec1_label_orig = MathTex(r"\vec{u}", color=PINK).next_to(vec1_orig.get_end(), UR, buff=0.1)
        vec2_label_orig = MathTex(r"\vec{w}", color=ORANGE).next_to(vec2_orig.get_end(), UL, buff=0.1)

        vecs_intro_group = VGroup(vec1_orig, vec2_orig, vec1_label_orig, vec2_label_orig)
        self.play(Create(vec1_orig), Create(vec2_orig), Write(vec1_label_orig), Write(vec2_label_orig))
        self.wait(1)

        # Apply transformation
        question_text = Text(
            "Most vectors change direction...", font_size=24
        ).next_to(matrix_A_tex_intro, RIGHT, buff=0.5)
        self.play(Write(question_text))

        # Apply matrix transformation to plane and vectors
        self.play(
            plane.animate.apply_matrix(matrix_A_val),
            vec1_orig.animate.apply_matrix(matrix_A_val),
            vec2_orig.animate.apply_matrix(matrix_A_val),
            vec1_label_orig.animate.next_to(vec1_orig.get_end(), UR, buff=0.1), # Keep label with vector
            vec2_label_orig.animate.next_to(vec2_orig.get_end(), UL, buff=0.1),
            run_time=3
        )
        self.wait(1)

        special_q_text = Text(
            "...but are there special vectors that only scale?", font_size=24
        ).next_to(question_text, DOWN, aligned_edge=LEFT)
        self.play(Write(special_q_text))
        self.wait(2)

        # Clear for next part of scene 1
        self.play(
            FadeOut(vecs_intro_group),
            FadeOut(question_text),
            FadeOut(special_q_text),
            FadeOut(matrix_A_tex_intro)
        )
        # Reset plane for clarity (or transform back)
        self.play(plane.animate.become(NumberPlane(
            x_range=[-5, 5, 1], y_range=[-4, 4, 1],
            x_length=10, y_length=7,
            background_line_style={"stroke_color": TEAL, "stroke_width": 2, "stroke_opacity": 0.5}
        ).add_coordinates().shift(DOWN*0.5)))
        self.wait(1)


        # --- SCENE 2: Introducing Eigenvectors and Eigenvalues ---
        self.play(FadeOut(title)) # Keep plane
        def_title = Text("Eigenvectors & Eigenvalues", font_size=32).to_edge(UP)
        self.play(Write(def_title))

        definition = MathTex(r"A\vec{v}", r" = ", r"\lambda\vec{v}").scale(1.5)
        definition.next_to(def_title, DOWN, buff=0.5)

        self.play(Write(definition))
        self.wait(1)

        explanation_parts = VGroup(
            Text("A: Our transformation matrix", font_size=24),
            Text("v: The Eigenvector (special direction)", font_size=24),
            Text("λ: The Eigenvalue (scaling factor)", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(definition, DOWN, buff=0.75)

        self.play(Write(explanation_parts[0]))
        self.wait(0.5)
        self.play(Write(explanation_parts[1]))
        self.wait(0.5)
        self.play(Write(explanation_parts[2]))
        self.wait(2)

        # Clear for the next section
        self.play(
            FadeOut(definition),
            FadeOut(explanation_parts)
        )
        self.wait(0.5)

        # --- SCENE 3: A Concrete Example ---
        # Use the matrix from user's original code for consistency if preferred
        matrix_A_val = np.array([[2, 1],
                                 [1, 2]])
        matrix_tex = MathTex(r"A = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}").to_corner(UL)
        self.play(Write(matrix_tex))
        self.wait(1)

        # Basis vectors
        i_hat = Vector([1,0], color=RED_C)
        j_hat = Vector([0,1], color=GREEN_C)
        i_hat_label = MathTex(r"\hat{\imath}", color=RED_C).next_to(i_hat.get_end(), DR, buff=0.1)
        j_hat_label = MathTex(r"\hat{\jmath}", color=GREEN_C).next_to(j_hat.get_end(), UR, buff=0.1)
        basis_group = VGroup(i_hat, j_hat, i_hat_label, j_hat_label)
        self.play(Create(i_hat), Create(j_hat), Write(i_hat_label), Write(j_hat_label))
        self.wait(1)

        # Transform basis vectors and plane
        transform_basis_text = Text("See how A transforms basis vectors & space:", font_size=20).to_corner(UR)
        self.play(Write(transform_basis_text))

        # Create copies for transformation labels
        Ai_hat_label_target_pos = np.dot(matrix_A_val, np.array([1,0]))
        Aj_hat_label_target_pos = np.dot(matrix_A_val, np.array([0,1]))

        Ai_hat_label = MathTex(r"A\hat{\imath}", color=RED_C).next_to(plane.c2p(*Ai_hat_label_target_pos), DR, buff=0.1)
        Aj_hat_label = MathTex(r"A\hat{\jmath}", color=GREEN_C).next_to(plane.c2p(*Aj_hat_label_target_pos), UR, buff=0.1)

        self.play(
            plane.animate.apply_matrix(matrix_A_val),
            i_hat.animate.apply_matrix(matrix_A_val),
            j_hat.animate.apply_matrix(matrix_A_val),
            ReplacementTransform(i_hat_label, Ai_hat_label),
            ReplacementTransform(j_hat_label, Aj_hat_label),
            run_time=3
        )
        self.wait(2)

        self.play(FadeOut(basis_group, Ai_hat_label, Aj_hat_label, transform_basis_text)) # i_hat_label and j_hat_label were transformed
        # Reset plane
        self.play(plane.animate.become(NumberPlane(
            x_range=[-5, 5, 1], y_range=[-4, 4, 1],
            x_length=10, y_length=7,
            background_line_style={"stroke_color": TEAL, "stroke_width": 2, "stroke_opacity": 0.5}
        ).add_coordinates().shift(DOWN*0.5)))
        self.wait(1)

        # Eigenvectors for A = [[2,1],[1,2]]
        # Eigenvalues are 3 and 1. Eigenvectors are [1,1] and [1,-1] (or multiples)
        eigenvalues, eigenvectors_raw = np.linalg.eig(matrix_A_val) # Raw eigenvectors are normalized columns

        # For better visualization, use simpler forms like [1,1] and [1,-1] and scale
        # Ensure order matches eigenvalues if manually defining
        # eigenvalue 3 corresponds to [1,1] (or [0.707, 0.707])
        # eigenvalue 1 corresponds to [-0.707, 0.707] (or [1,-1] if we flip signs)

        # Let's find which eigenvalue is which to assign colors correctly
        lambda_3_idx = np.argmax(eigenvalues)
        lambda_1_idx = np.argmin(eigenvalues)

        ev_for_lambda_3 = eigenvectors_raw[:, lambda_3_idx]
        ev_for_lambda_1 = eigenvectors_raw[:, lambda_1_idx]

        # Normalize for consistent appearance (optional, but good for base vector)
        # Then scale for visibility. Choose a scale factor.
        vis_scale = 2.0

        # Eigenvector 1 (for eigenvalue 3)
        # We know it's along [1,1] direction. Take the one from np.linalg.eig and scale.
        # Ensure it points into first quadrant if possible for consistency
        if ev_for_lambda_3[0] < 0: ev_for_lambda_3 *= -1 # Make x positive
        v1 = Vector(ev_for_lambda_3 * vis_scale, color=BLUE_C)
        v1_label = MathTex(r"\vec{v}_1", color=BLUE_C).next_to(v1.get_end(), UP, buff=0.1)
        lambda1_val = eigenvalues[lambda_3_idx]
        lambda1_tex = MathTex(f"\\lambda_1 = {lambda1_val:.0f}", color=BLUE_C).to_corner(DL).shift(UP*1.5)

        self.play(Create(v1), Write(v1_label), Write(lambda1_tex))
        self.wait(1)

        v1_transformed = v1.copy().apply_matrix(matrix_A_val) # This will be v1 scaled by lambda1
        # For clarity, explicitly show it's lambda*v
        # v1_transformed_target = Vector(lambda1_val * ev_for_lambda_3 * vis_scale, color=BLUE_D, stroke_width=7)

        self.play(Transform(v1, v1_transformed, run_time=2)) # v1 becomes A*v1
        av1_label = MathTex(r"A\vec{v}_1 = \lambda_1\vec{v}_1", color=BLUE_C).next_to(v1.get_end(), UP, buff=0.1)
        self.play(Transform(v1_label, av1_label))
        self.wait(2)

        # Eigenvector 2 (for eigenvalue 1)
        # Along [1,-1] direction.
        if ev_for_lambda_1[0] < 0: ev_for_lambda_1 *= -1 # Make x positive, so points to quadrant IV
        v2 = Vector(ev_for_lambda_1 * vis_scale, color=YELLOW_C)
        v2_label = MathTex(r"\vec{v}_2", color=YELLOW_C).next_to(v2.get_end(), DOWN, buff=0.1)
        lambda2_val = eigenvalues[lambda_1_idx]
        lambda2_tex = MathTex(f"\\lambda_2 = {lambda2_val:.0f}", color=YELLOW_C).next_to(lambda1_tex, DOWN, aligned_edge=LEFT)

        self.play(Create(v2), Write(v2_label), Write(lambda2_tex))
        self.wait(1)

        v2_transformed = v2.copy().apply_matrix(matrix_A_val)
        # v2_transformed_target = Vector(lambda2_val * ev_for_lambda_1 * vis_scale, color=YELLOW_D, stroke_width=7)

        self.play(Transform(v2, v2_transformed, run_time=2))
        av2_label = MathTex(r"A\vec{v}_2 = \lambda_2\vec{v}_2", color=YELLOW_C).next_to(v2.get_end(), DOWN, buff=0.1)
        self.play(Transform(v2_label, av2_label))
        self.wait(2)

        # Keep transformed vectors v1 and v2 on screen.
        # Group them for easier FadeOut later
        eigen_vis_group = VGroup(v1, v2, v1_label, v2_label, lambda1_tex, lambda2_tex)


        # --- SCENE 4: The Power of Eigenbasis (Simplified version) ---
        # Clear some space but keep eigenvectors if needed
        self.play(FadeOut(matrix_tex)) # def_title is still up

        eigen_basis_title = Text("Eigenvectors as a 'Natural' Basis", font_size=28).to_edge(UP, buff=0.2)
        self.play(Transform(def_title, eigen_basis_title))

        arbitrary_vec_np = np.array([0.5, 1.5]) # A different vector
        w = Vector(arbitrary_vec_np, color=WHITE)
        w_label = MathTex(r"\vec{w}", color=WHITE).next_to(w.get_end(), RIGHT, buff=0.1)
        self.play(Create(w), Write(w_label))
        self.wait(1)

        # Show transformation of arbitrary vector
        w_transformed = w.copy().apply_matrix(matrix_A_val)
        # w_transformed_target = Vector(np.dot(matrix_A_val, arbitrary_vec_np), color=GRAY, stroke_width=7)

        how_w_transforms_text = Text(
            "Transforming w directly can be complex...", font_size=20
        ).to_corner(UR).shift(LEFT*2)
        self.play(Write(how_w_transforms_text))
        self.play(Transform(w, w_transformed, run_time=2))
        Aw_label = MathTex(r"A\vec{w}", color=WHITE).next_to(w.get_end(), RIGHT, buff=0.1)
        self.play(Transform(w_label, Aw_label))
        self.wait(1)
        self.play(FadeOut(how_w_transforms_text))


        # Reset w for decomposition explanation
        self.play(
            Transform(w, Vector(arbitrary_vec_np, color=WHITE)), # Transform w back
            Transform(w_label, MathTex(r"\vec{w}", color=WHITE).next_to(w.get_end(), RIGHT, buff=0.1))
        )
        self.wait(0.5)

        decomp_text = Text(
            "But if w is sum of scaled eigenvectors: w = c₁v₁ + c₂v₂", font_size=20
        ).to_corner(UR)
        self.play(Write(decomp_text))

        # Decompose w: w = c1*v1_unit + c2*v2_unit (using UNNORMALIZED eigenvectors from before)
        # eigenvectors_raw columns are already normalized. Let's use those.
        # v1_unit = eigenvectors_raw[:, lambda_3_idx]
        # v2_unit = eigenvectors_raw[:, lambda_1_idx]
        # For actual decomposition, we need the eigenvectors that are columns of `eigenvectors_raw`
        # coeffs = np.linalg.solve(eigenvectors_raw, arbitrary_vec_np)
        # c1_val, c2_val = coeffs[lambda_3_idx], coeffs[lambda_1_idx] # Careful with indexing if reordered

        # To be safe, use the specific eigenvectors chosen (scaled versions don't matter for lin. combination if consistent)
        # For the matrix [[2,1],[1,2]], eigenvectors are [1,1] and [1,-1] (or their multiples)
        # Let v1_basis = [1,1], v2_basis = [1,-1]
        eig_basis_matrix = np.array([[1, 1], [1, -1]]).T # Columns are eigenvectors
        coeffs = np.linalg.solve(eig_basis_matrix, arbitrary_vec_np)
        c1_val, c2_val = coeffs[0], coeffs[1]


        # Components (using the scaled v1, v2 from visualization for consistency)
        # This is a bit tricky if v1, v2 were scaled arbitrarily. Let's use unit versions then scale.
        v1_unit_dir = ev_for_lambda_3
        v2_unit_dir = ev_for_lambda_1

        comp1 = Vector(c1_val * v1_unit_dir * vis_scale, color=BLUE_A, stroke_width=3) # Scale by vis_scale to match v1
        comp2_start = c1_val * v1_unit_dir * vis_scale
        comp2 = Vector(c2_val * v2_unit_dir * vis_scale, color=YELLOW_A, stroke_width=3).shift(comp2_start)

        comp1_label = MathTex(f"{c1_val:.1f}\\vec{{v}}_1", color=BLUE_A, font_size=24).next_to(comp1.get_end(), UL, buff=0.05)
        comp2_label = MathTex(f"{c2_val:.1f}\\vec{{v}}_2", color=YELLOW_A, font_size=24).next_to(comp2.get_end(), UR, buff=0.05)

        components_group = VGroup(comp1, comp2, comp1_label, comp2_label)
        self.play(FadeOut(w, w_label), Create(comp1), Write(comp1_label)) # Show w being built
        self.play(Create(comp2), Write(comp2_label))
        self.wait(1)

        # Transform components
        transform_text = Text(
            "Then Aw = c₁λ₁v₁ + c₂λ₂v₂ (just scaling components!)", font_size=20
        ).next_to(decomp_text, DOWN, aligned_edge=RIGHT)
        self.play(Write(transform_text))

        # Transformed components (again, scale by vis_scale for consistency with v1, v2 visuals)
        t_comp1 = Vector(c1_val * lambda1_val * v1_unit_dir * vis_scale, color=BLUE_D, stroke_width=5)
        t_comp2_start = c1_val * lambda1_val * v1_unit_dir * vis_scale
        t_comp2 = Vector(c2_val * lambda2_val * v2_unit_dir * vis_scale, color=YELLOW_D, stroke_width=5).shift(t_comp2_start)

        t_comp1_label = MathTex(f"{c1_val:.1f}\\lambda_1\\vec{{v}}_1", color=BLUE_D, font_size=24).next_to(t_comp1.get_end(), UL, buff=0.05)
        t_comp2_label = MathTex(f"{c2_val:.1f}\\lambda_2\\vec{{v}}_2", color=YELLOW_D, font_size=24).next_to(t_comp2.get_end(), UR, buff=0.05)

        transformed_components_group = VGroup(t_comp1, t_comp2, t_comp1_label, t_comp2_label)

        self.play(
            ReplacementTransform(comp1, t_comp1),
            ReplacementTransform(comp2, t_comp2),
            ReplacementTransform(comp1_label, t_comp1_label),
            ReplacementTransform(comp2_label, t_comp2_label),
            run_time=2
        )
        self.wait(2)

        # Show the final transformed vector sum
        final_Aw = Vector(np.dot(matrix_A_val, arbitrary_vec_np), color=WHITE, stroke_width=7)
        final_Aw_label = MathTex("A\\vec{w}", color=WHITE).next_to(final_Aw.get_end(), RIGHT, buff=0.1)

        # Animate components adding up to final_Aw (optional, can be complex)
        # For now, just show final_Aw on top
        self.play(FadeOut(transformed_components_group), Create(final_Aw), Write(final_Aw_label))
        self.wait(2)


        self.play(
            FadeOut(eigen_vis_group), FadeOut(decomp_text), FadeOut(transform_text),
            FadeOut(final_Aw), FadeOut(final_Aw_label)
        )
        self.wait(0.5)


        # --- SCENE 5: Finding Them – The Characteristic Equation ---
        derivation_title = Text("How to Find Eigenvalues?", font_size=32).to_edge(UP)
        self.play(Transform(def_title, derivation_title)) # def_title was eigen_basis_title

        eq_y_pos = def_title.get_bottom()[1] - 0.75

        eq1 = MathTex(r"A\vec{v} = \lambda\vec{v}").move_to(UP * eq_y_pos / FRAME_HEIGHT * config.frame_height) # Adjust y based on frame
        self.play(Write(eq1))
        self.wait(1)

        eq2 = MathTex(r"A\vec{v} - \lambda\vec{v} = \vec{0}")
        eq2.next_to(eq1, DOWN, buff=0.75) # Position based on previous equation
        self.play(TransformMatchingTex(eq1.copy(), eq2, path_arc=PI/2)) # Smooth transform
        self.wait(1)

        eq3 = MathTex(r"A\vec{v} - \lambda I\vec{v} = \vec{0}")
        eq3.next_to(eq2, DOWN, buff=0.75)
        explain_I = Text("Insert Identity Matrix I (doesn't change λv)", font_size=20, color=GREEN)
        explain_I.next_to(eq3, RIGHT, buff=0.5)
        self.play(TransformMatchingTex(eq2.copy(), eq3), Write(explain_I))
        self.wait(1)
        self.play(FadeOut(explain_I))

        eq4 = MathTex(r"(A - \lambda I)\vec{v} = \vec{0}")
        eq4.next_to(eq3, DOWN, buff=0.75)
        self.play(TransformMatchingTex(eq3.copy(), eq4))
        self.wait(1)

        explanation_text = Text(
            "For non-trivial solutions (v ≠ 0), (A - λI) must be a singular matrix.",
            font_size=24
        ).next_to(eq4, DOWN, buff=0.5)
        self.play(Write(explanation_text))
        self.wait(1.5)

        det_eq = MathTex(r"\det(A - \lambda I) = 0")
        det_eq.next_to(explanation_text, DOWN, buff=0.5)
        det_text = Text("This means its determinant is zero.", font_size=24, color=YELLOW)
        det_text.next_to(det_eq, RIGHT, buff=0.3)
        self.play(Write(det_eq), Write(det_text))
        self.wait(1)

        poly_text = Text("This is the Characteristic Polynomial. Solve for λ!", font_size=24)
        poly_text.next_to(det_eq, DOWN, buff=0.5)
        self.play(Write(poly_text))
        self.wait(2)

        # Group derivation elements for fadeout
        derivation_group = VGroup(eq1, eq2, eq3, eq4, explanation_text, det_eq, det_text, poly_text)
        self.play(FadeOut(derivation_group))
        self.wait(0.5)


        # --- SCENE 6: Why We Care & Conclusion ---
        # Reuse derivation_title (which is def_title transformed)
        conclusion_title_text = Text("Why Are Eigenvalues Important?", font_size=32)
        conclusion_title_text.to_edge(UP)
        self.play(Transform(def_title, conclusion_title_text))


        applications = VGroup(
            Text("- Reveal fundamental properties of transformations", font_size=28),
            Text("- Principal Component Analysis (PCA) in Data Science", font_size=28),
            Text("- Quantum Mechanics (energy states)", font_size=28),
            Text("- Vibrational Analysis (natural frequencies)", font_size=28),
            Text("- Stability of systems, PageRank, and much more!", font_size=28)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).next_to(def_title, DOWN, buff=0.7)

        for app in applications:
            self.play(AddTextLetterByLetter(app), run_time=1.5)
            self.wait(0.5)

        self.wait(3)

        final_message = Text("They show the 'soul' of a matrix.", font_size=30, color=GOLD)
        final_message.next_to(applications, DOWN, buff=1.0)
        self.play(Write(final_message))
        self.wait(2)

        self.play(
            FadeOut(def_title), # This is conclusion_title_text now
            FadeOut(applications),
            FadeOut(final_message),
            FadeOut(plane), # Fade out the number plane
            FadeOut(matrix_tex) # If it's still there (it was faded out earlier)
        )
        self.wait(1)
        # Final title screen again
        self.play(Write(title.move_to(ORIGIN))) # Reuse initial title, centered
        self.wait(3)
        self.play(FadeOut(title))
