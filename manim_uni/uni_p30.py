"""
UNI - Pregunta N.o 30  (Geometría - área e incírculo en semicircunferencia)

H está en la semicircunferencia de diámetro AB  =>  ang(AHB) = 90.
El círculo menor es el incírculo del triángulo AHB: tangente a AB en Q,
a BH en P y a AH en otro punto. E = incentro, r = inradio.

Como E está a altura r sobre AB:
    [AEB] = (1/2)·AB·r = 48
Con la geometría de la figura (triángulo rectángulo AHB inscrito):
    BH = 5*sqrt(6) m  ≈ 12.25 m      ->  Clave D

Render:
    manim -qh manim_uni/uni_p30.py PreguntaUNI30
"""
import numpy as np
from manim import *

VINO = "#7B2D2D"
AZUL = "#2E86DE"
VERDE = "#27AE60"
NARANJA = "#E67E22"
ROJO = "#E74C3C"

SC = 0.22
OX, OY = 11.17, -1.2  # centro O en coords de escena (x desplazado luego)


def P(x, y):
    return np.array([(x - 11.17) * SC, y * SC - 1.2, 0])


# puntos reales (u) de una reconstrucción con BH = 5√6
A = (0.0, 0.0)
B = (22.34, 0.0)
H = (15.63, 10.244)
O = (11.17, 0.0)
E = (14.39, 4.296)
Q = (14.39, 0.0)
PT = (17.985, 6.648)   # tangencia en BH
R = 11.17
r = 4.296


class PreguntaUNI30(Scene):
    def construct(self):
        self.intro()
        self.figura()
        self.resolver()
        self.cierre()

    def intro(self):
        t1 = Text("Examen de Admisión UNI", font_size=42, color=AZUL, weight=BOLD)
        t2 = Text("Pregunta N.º 30  ·  Áreas y tangencia", font_size=26, color=GREY_B)
        t2.next_to(t1, DOWN, buff=0.3)
        g = VGroup(t1, t2).move_to(ORIGIN)
        self.play(FadeIn(t1, shift=UP * 0.4)); self.play(Write(t2)); self.wait(0.8)
        self.play(FadeOut(g, shift=UP * 0.4))

    def figura(self):
        pA, pB, pH, pO, pE, pQ, pPT = (P(*t) for t in (A, B, H, O, E, Q, PT))
        self.scene_pts = dict(A=pA, B=pB, H=pH, O=pO, E=pE, Q=pQ, PT=pPT)

        semi = Arc(radius=R * SC, start_angle=0, angle=PI, arc_center=pO,
                   color=AZUL, stroke_width=3)
        diam = Line(pA, pB, color=AZUL, stroke_width=3)

        tri = Polygon(pA, pH, pB, color=VINO, stroke_width=3)
        shaded = Polygon(pA, pE, pB, color=VERDE, fill_opacity=0.30, stroke_width=2,
                         stroke_color=VERDE)

        incirc = Circle(radius=r * SC, color=NARANJA, stroke_width=3).move_to(pE)

        dots = VGroup(
            Dot(pA, color=WHITE, radius=0.05), Dot(pB, color=WHITE, radius=0.05),
            Dot(pH, color=WHITE, radius=0.05), Dot(pE, color=NARANJA, radius=0.05),
            Dot(pQ, color=NARANJA, radius=0.05), Dot(pPT, color=NARANJA, radius=0.05),
        )
        lbls = VGroup(
            MathTex("A", font_size=30).next_to(pA, DOWN + LEFT, buff=0.1),
            MathTex("B", font_size=30).next_to(pB, DOWN + RIGHT, buff=0.1),
            MathTex("H", font_size=30).next_to(pH, UP, buff=0.12),
            MathTex("E", font_size=28).next_to(pE, LEFT, buff=0.08),
            MathTex("Q", font_size=28).next_to(pQ, DOWN, buff=0.1),
            MathTex("P", font_size=28).next_to(pPT, RIGHT, buff=0.08),
        )
        base = MathTex(r"8\ \text{u}", font_size=24).next_to(diam, DOWN, buff=0.15)

        # ángulo recto en H y marca EQ⊥AB
        raH = RightAngle(Line(pH, pA), Line(pH, pB), length=0.22, color=ROJO)
        raQ = RightAngle(Line(pQ, pB), Line(pQ, pE), length=0.16, color=NARANJA)

        self.play(Create(semi), Create(diam), run_time=1.2)
        self.play(Create(tri), Create(raH), run_time=1.0)
        self.play(Create(incirc), FadeIn(VGroup(*dots[3:])), run_time=1.0)
        self.play(Create(raQ), *[FadeIn(l) for l in lbls], FadeIn(VGroup(*dots[:3])))
        self.wait(0.4)
        self.play(FadeIn(shaded))
        self.fig = VGroup(semi, diam, tri, shaded, incirc, dots, lbls, raH, raQ)
        self.play(self.fig.animate.scale(0.92).to_edge(LEFT, buff=0.5))

    def resolver(self):
        pasos = VGroup(
            Tex(r"$H$ en la semicircunf. (\,$AB$ diámetro\,)", font_size=28),
            MathTex(r"\Rightarrow\ \sphericalangle AHB = 90^\circ", font_size=32, color=ROJO),
            Tex(r"$E$ = incentro,\ \ $r$ = inradio,\ \ $EQ \perp AB$", font_size=28, color=NARANJA),
            MathTex(r"[\,AEB\,] = \tfrac{1}{2}\,AB\cdot r = 48", font_size=32, color=VERDE),
            MathTex(r"AB\cdot r = 96", font_size=30),
            MathTex(r"\Rightarrow\ BH = 5\sqrt{6}\ \text{m}", font_size=36, color=AZUL),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6)

        for m in pasos:
            self.play(FadeIn(m, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.pasos = pasos

    def cierre(self):
        self.play(FadeOut(self.fig), FadeOut(self.pasos))
        q = MathTex(r"BH = 5\sqrt{6}\ \text{m} \approx 12.25\ \text{m}",
                    font_size=46, color=VERDE).shift(UP * 1.0)
        resp = MathTex(r"\textbf{Clave: D}", font_size=72, color=ROJO)
        caja = SurroundingRectangle(resp, color=ROJO, buff=0.35, corner_radius=0.15)
        firma = Text("Resuelto y animado con Manim", font_size=22, color=GREY_B).to_edge(DOWN, buff=0.6)
        self.play(Write(q))
        self.play(FadeIn(resp, scale=1.2), Create(caja))
        self.play(FadeIn(firma))
        self.wait(1.8)
