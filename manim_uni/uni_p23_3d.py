"""
UNI - Pregunta N.o 23  (Geometría del espacio - superficies semiesféricas)  [3D]

Dos semiesferas de radios R y r. AP = 2*sqrt(13), BP = 4.
La semiesfera menor tiene a OB como diámetro (r = R/2), con O = centro
de la mayor = punto medio de AB.

Solución:
    OB diámetro de la esfera menor, P sobre ella  =>  ang(OPB) = 90
    Triángulo rectángulo OPB:  OP^2 + PB^2 = OB^2 = R^2
    PO es mediana de APB:  OP^2 = (2 AP^2 + 2 BP^2 - AB^2)/4 = 34 - R^2
    =>  R^2 = (34 - R^2) + 16  =>  R = 5     (sale un 3-4-5: OP=3, PB=4, OB=5)
    Área semiesfera mayor = 2*pi*R^2 = 50 pi      ->  Clave E

Render:
    manim -qh manim_uni/uni_p23_3d.py Problema3D
"""
import numpy as np
from manim import *

VINO = "#7B2D2D"
AZUL = "#2E86DE"
VERDE = "#27AE60"
NARANJA = "#E67E22"
ROJO = "#E74C3C"

SCALE = 0.45


def V(x, y, z):
    return np.array([x, y, z]) * SCALE


def hemi(center, rad, color):
    cx, cy, cz = center
    s = Surface(
        lambda u, v: V(cx + rad * np.sin(v) * np.cos(u),
                       cy + rad * np.sin(v) * np.sin(u),
                       cz + rad * np.cos(v)),
        u_range=[0, TAU], v_range=[0, PI / 2],
        resolution=(28, 14), checkerboard_colors=False,
        fill_opacity=0.14, stroke_width=0.6,
    )
    s.set_fill(color, opacity=0.14)
    s.set_stroke(color, width=0.6, opacity=0.45)
    return s


class Problema3D(ThreeDScene):
    def construct(self):
        # puntos (en unidades reales R=5, r=2.5)
        A = V(-5, 0, 0); O = V(0, 0, 0); B = V(5, 0, 0)
        O1 = V(2.5, 0, 0); P = V(1.8, 0, 2.4)

        self.set_camera_orientation(phi=68 * DEGREES, theta=-58 * DEGREES, zoom=0.95)

        titulo = Text("UNI · Pregunta 23  —  Semiesferas (3D)",
                      font_size=30, color=AZUL, weight=BOLD).to_edge(UP, buff=0.35)
        self.add_fixed_in_frame_mobjects(titulo)
        self.play(FadeIn(titulo))

        # ---- semiesfera mayor ----
        big = hemi((0, 0, 0), 5, VINO)
        base_big = Circle(radius=5 * SCALE, color=VINO, stroke_width=2)
        self.play(Create(base_big), run_time=0.8)
        self.play(Create(big), run_time=1.6)

        # diámetro y puntos A, O, B
        diam = DashedLine(A, B, color=GREY_B, stroke_width=2)
        dA = Dot3D(A, color=WHITE, radius=0.06)
        dO = Dot3D(O, color=YELLOW, radius=0.06)
        dB = Dot3D(B, color=WHITE, radius=0.06)
        lA = MathTex("A", font_size=34).next_to(A, LEFT, buff=0.15)
        lB = MathTex("B", font_size=34).next_to(B, RIGHT, buff=0.15)
        lO = MathTex("O", font_size=30, color=YELLOW).next_to(O, DOWN + LEFT, buff=0.12)
        self.add_fixed_orientation_mobjects(lA, lB, lO)
        self.play(Create(diam), FadeIn(dA), FadeIn(dO), FadeIn(dB),
                  Write(lA), Write(lB), Write(lO))
        self.wait(0.4)

        # ---- semiesfera menor (diámetro OB) ----
        small = hemi((2.5, 0, 0), 2.5, NARANJA)
        base_small = Circle(radius=2.5 * SCALE, color=NARANJA, stroke_width=2).move_to(O1)
        self.play(Create(base_small), Create(small), run_time=1.4)

        dP = Dot3D(P, color=ROJO, radius=0.07)
        lP = MathTex("P", font_size=34, color=ROJO).next_to(P, UP, buff=0.15)
        self.add_fixed_orientation_mobjects(lP)
        self.play(GrowFromCenter(dP), Write(lP))

        # ---- segmentos AP, BP ----
        segAP = Line(A, P, color=AZUL, stroke_width=4)
        segBP = Line(B, P, color=AZUL, stroke_width=4)
        lAP = MathTex(r"2\sqrt{13}", font_size=26, color=AZUL).move_to(
            self.mid(A, P) + V(-0.3, 0, 0.8))
        lBP = MathTex("4", font_size=26, color=AZUL).move_to(self.mid(B, P) + V(0.6, 0, 0.4))
        self.add_fixed_orientation_mobjects(lAP, lBP)
        self.play(Create(segAP), Create(segBP), Write(lAP), Write(lBP))
        self.wait(0.5)

        # ---- mediana OP y triángulo 3-4-5 ----
        segOP = Line(O, P, color=VERDE, stroke_width=5)
        lOP = MathTex("3", font_size=28, color=VERDE).move_to(self.mid(O, P) + V(-0.6, 0, 0))
        self.add_fixed_orientation_mobjects(lOP)
        self.play(Create(segOP), Write(lOP))

        # resaltar triángulo OPB (3-4-5, recto en P)
        tri = Polygon(O, P, B, color=ROJO, fill_opacity=0.18, stroke_width=3)
        ang90 = MathTex(r"90^\circ", font_size=24, color=ROJO).move_to(P + V(0.2, 0, -0.7))
        self.add_fixed_orientation_mobjects(ang90)
        self.play(Create(tri), Write(ang90))
        self.wait(0.6)

        # ---- panel de solución (fijo en pantalla) ----
        panel = VGroup(
            MathTex(r"OB \text{ diám. menor} \Rightarrow \sphericalangle OPB = 90^\circ",
                    font_size=28, color=NARANJA),
            MathTex(r"OP^2 + PB^2 = OB^2 = R^2", font_size=30),
            MathTex(r"OP^2 = \tfrac{2AP^2 + 2BP^2 - AB^2}{4} = 34 - R^2",
                    font_size=28, color=VERDE),
            MathTex(r"R^2 = (34 - R^2) + 16 \;\Rightarrow\; R = 5", font_size=30, color=AZUL),
            MathTex(r"\triangle OPB:\ 3\text{-}4\text{-}5", font_size=28, color=ROJO),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        panel.to_corner(DR, buff=0.4)
        self.add_fixed_in_frame_mobjects(panel)
        for m in panel:
            self.play(FadeIn(m, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        # giro ambiental para apreciar el 3D
        self.begin_ambient_camera_rotation(rate=0.35)
        self.wait(4)
        self.stop_ambient_camera_rotation()

        # ---- respuesta final ----
        self.play(*[FadeOut(m) for m in [panel, segAP, segBP, segOP, tri,
                                         lAP, lBP, lOP, ang90]])
        area = MathTex(r"S = 2\pi R^2 = 2\pi(5)^2 = 50\pi\ \text{cm}^2",
                       font_size=40, color=VERDE).to_edge(DOWN, buff=1.2)
        clave = MathTex(r"\textbf{Clave: E}", font_size=48, color=ROJO).to_edge(DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(area, clave)
        self.play(Write(area))
        self.play(FadeIn(clave, scale=1.2))
        self.wait(2)

    @staticmethod
    def mid(p, q):
        return (p + q) / 2
