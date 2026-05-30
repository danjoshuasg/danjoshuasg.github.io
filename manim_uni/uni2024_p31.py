"""
UNI 2024-1 - Pregunta N.o 31  (Geometría - ángulos)

Triángulo AED. F, E, D colineales. EC = CD y AB = BE.
m(AEF) = 2 m(BEC). Hallar m(BEC).

Solución (x = m(BEC)):
    AB = BE  =>  ang(EAB) = ang(AEB) = a      (isósceles)
    EC = CD  =>  ang(EDC) = ang(CED) = b      (isósceles)
    ang(AEF) = a + b      (ángulo exterior del triángulo AED en E)
    ang(AEF) = 2x         =>  a + b = 2x
    ang(AED) = a + x + b = 3x
    F,E,D colineales  =>  ang(AED) + ang(AEF) = 180
                          3x + 2x = 180  =>  x = 36

Respuesta: A) 36°

Render:
    manim -qh manim_uni/uni2024_p31.py PreguntaUNI31
"""
import numpy as np
from manim import *

VINO = "#7B2D2D"
AZUL = "#2E86DE"
VERDE = "#27AE60"
NARANJA = "#E67E22"
ROJO = "#E74C3C"
MORADO = "#8E44AD"

# ---- coordenadas exactas (en unidades) que cumplen todas las condiciones ----
U = {
    "A": (0.0, 0.0),
    "B": (3.375, 0.0),
    "C": (5.828, 0.0),
    "D": (10.0, 0.0),
    "E": (3.375, 3.375),
    "F": (0.725, 4.725),
}
SX, DX, DY = 0.5, -1.8, -1.0


def P(name):
    x, y = U[name]
    return np.array([(x - 5) * SX + DX, y * SX + DY, 0])


def ticks(p, q, n=1, color=YELLOW):
    mid = (p + q) / 2
    d = normalize(q - p)
    perp = np.array([-d[1], d[0], 0])
    g = VGroup()
    spacing = 0.10
    start = -(n - 1) / 2 * spacing
    for i in range(n):
        c = mid + d * (start + i * spacing)
        g.add(Line(c - perp * 0.11, c + perp * 0.11, color=color, stroke_width=4))
    return g


class PreguntaUNI31(Scene):
    def construct(self):
        self.intro()
        self.figura()
        self.datos()
        self.resolver()
        self.cierre()

    def intro(self):
        t1 = Text("Examen de Admisión UNI 2024-1", font_size=40, color=AZUL, weight=BOLD)
        t2 = Text("Pregunta N.º 31  ·  Geometría", font_size=26, color=GREY_B)
        t2.next_to(t1, DOWN, buff=0.3)
        g = VGroup(t1, t2).move_to(ORIGIN)
        self.play(FadeIn(t1, shift=UP * 0.4)); self.play(Write(t2)); self.wait(0.8)
        self.play(FadeOut(g, shift=UP * 0.4))

    def figura(self):
        A, B, C, D, E, F = (P(k) for k in "ABCDEF")
        self.pts = dict(A=A, B=B, C=C, D=D, E=E, F=F)

        base = Line(A, D, color=VINO, stroke_width=3)
        EA = Line(E, A, color=VINO, stroke_width=3)
        ED_F = Line(F, D, color=VINO, stroke_width=3)  # recta F-E-D
        EB = Line(E, B, color=VINO, stroke_width=3)
        EC = Line(E, C, color=VINO, stroke_width=3)

        dots = VGroup(*[Dot(p, color=VINO, radius=0.05) for p in (A, B, C, D, E, F)])
        lbls = VGroup(
            MathTex("A", font_size=30).next_to(A, DOWN, buff=0.15),
            MathTex("B", font_size=30).next_to(B, DOWN, buff=0.15),
            MathTex("C", font_size=30).next_to(C, DOWN, buff=0.15),
            MathTex("D", font_size=30).next_to(D, DOWN, buff=0.15),
            MathTex("E", font_size=30).next_to(E, UP + RIGHT, buff=0.10),
            MathTex("F", font_size=30).next_to(F, UP, buff=0.12),
        )

        self.play(Create(ED_F), Create(EA), Create(base), run_time=1.2)
        self.play(Create(EB), Create(EC), run_time=0.9)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.1),
                  *[FadeIn(l) for l in lbls], run_time=1.0)
        self.wait(0.4)
        self.fig = VGroup(base, EA, ED_F, EB, EC, dots, lbls)

    def datos(self):
        A, B, C, D, E = (self.pts[k] for k in "ABCDE")
        # marcas de congruencia
        t_AB = ticks(A, B, 1, ROJO)
        t_BE = ticks(B, E, 1, ROJO)
        t_EC = ticks(E, C, 2, VERDE)
        t_CD = ticks(C, D, 2, VERDE)

        panel = VGroup(
            Text("Datos", font_size=28, color=NARANJA, weight=BOLD),
            MathTex(r"AB = BE", font_size=34, color=ROJO),
            MathTex(r"EC = CD", font_size=34, color=VERDE),
            MathTex(r"F,\,E,\,D \text{ colineales}", font_size=32),
            MathTex(r"m\sphericalangle AEF = 2\,m\sphericalangle BEC", font_size=32, color=AZUL),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8).shift(UP * 0.3)

        self.play(FadeIn(panel[0], shift=UP * 0.2))
        self.play(Create(t_AB), Create(t_BE), Write(panel[1]))
        self.play(Create(t_EC), Create(t_CD), Write(panel[2]))
        self.play(Write(panel[3]))
        self.play(Write(panel[4]))
        self.wait(1.0)
        self.play(FadeOut(panel), FadeOut(VGroup(t_AB, t_BE, t_EC, t_CD)))

    def resolver(self):
        A, B, C, D, E, F = (self.pts[k] for k in "ABCDEF")

        # arcos de ángulo en E
        ang_AEB = Angle(Line(E, A), Line(E, B), radius=0.55, color=ROJO)
        ang_BEC = Angle(Line(E, B), Line(E, C), radius=0.78, color=AZUL)
        ang_CED = Angle(Line(E, C), Line(E, D), radius=0.55, color=VERDE)
        ang_AEF = Angle(Line(E, F), Line(E, A), radius=0.40, color=NARANJA)

        la = MathTex(r"\alpha", font_size=26, color=ROJO).move_to(
            Angle(Line(E, A), Line(E, B), radius=0.95).point_from_proportion(0.5))
        lx = MathTex(r"x", font_size=26, color=AZUL).move_to(
            Angle(Line(E, B), Line(E, C), radius=1.15).point_from_proportion(0.5))
        lb = MathTex(r"\beta", font_size=26, color=VERDE).move_to(
            Angle(Line(E, C), Line(E, D), radius=0.95).point_from_proportion(0.5))
        l2x = MathTex(r"2x", font_size=24, color=NARANJA).move_to(
            Angle(Line(E, F), Line(E, A), radius=0.72).point_from_proportion(0.5))

        self.play(Create(ang_AEB), FadeIn(la), Create(ang_CED), FadeIn(lb))
        self.play(Create(ang_BEC), FadeIn(lx))
        self.play(Create(ang_AEF), FadeIn(l2x))
        self.wait(0.4)

        pasos = VGroup(
            MathTex(r"AB=BE \Rightarrow \alpha = m\sphericalangle AEB", font_size=30, color=ROJO),
            MathTex(r"EC=CD \Rightarrow \beta = m\sphericalangle CED", font_size=30, color=VERDE),
            MathTex(r"m\sphericalangle AEF = \alpha + \beta = 2x", font_size=32, color=NARANJA),
            MathTex(r"m\sphericalangle AED = \alpha + x + \beta = 3x", font_size=32),
            MathTex(r"\underbrace{3x}_{AED} + \underbrace{2x}_{AEF} = 180^\circ", font_size=34, color=AZUL),
            MathTex(r"5x = 180^\circ \;\Rightarrow\; x = 36^\circ", font_size=36, color=ROJO),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(RIGHT, buff=0.7)

        for m in pasos:
            self.play(FadeIn(m, shift=UP * 0.15), run_time=0.65)
        self.wait(1.2)
        self.anggroup = VGroup(ang_AEB, ang_BEC, ang_CED, ang_AEF, la, lx, lb, l2x)
        self.pasos = pasos

    def cierre(self):
        self.play(FadeOut(self.fig), FadeOut(self.anggroup), FadeOut(self.pasos))
        q = MathTex(r"m\sphericalangle BEC = 36^\circ", font_size=64, color=VERDE).shift(UP * 1.0)
        resp = MathTex(r"\textbf{Clave: A}", font_size=72, color=ROJO)
        caja = SurroundingRectangle(resp, color=ROJO, buff=0.35, corner_radius=0.15)
        firma = Text("Resuelto y animado con Manim", font_size=22, color=GREY_B).to_edge(DOWN, buff=0.6)
        self.play(Write(q))
        self.play(FadeIn(resp, scale=1.2), Create(caja))
        self.play(FadeIn(firma))
        self.wait(1.8)
