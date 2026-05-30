"""
UNI 2025 - Pregunta N.o 22 (Suficiencia de datos)

Se desea hallar el area del triangulo ABC. En el rectangulo ADEC,
B esta sobre el lado superior DE y AC = 8 u.

    I.  AE = 10 u            (diagonal del rectangulo)
    II. Area(ADEC) = 48 u^2

Como B esta sobre DE, la altura del triangulo ABC respecto a AC
es la altura h del rectangulo  =>  Area(ABC) = 1/2 * 8 * h = 4h.
Basta conocer h.

    I  ->  8^2 + h^2 = 10^2  =>  h = 6  =>  Area = 24   (suficiente)
    II ->  8 * h = 48        =>  h = 6  =>  Area = 24   (suficiente)

Respuesta: D) Cada una de las informaciones por separado es suficiente.

Render:
    manim -qh manim_uni/uni2025_p22.py PreguntaUNI22
"""
import numpy as np
from manim import *

VINO = "#7B2D2D"
AZUL = "#2E86DE"
VERDE = "#27AE60"
NARANJA = "#E67E22"
ROJO = "#E74C3C"

S = 0.5  # escala: 8u -> 4.0, 6u -> 3.0


def corner_mark(corner, ix, iy, color=VINO):
    sq = Square(side_length=0.20, color=color, stroke_width=2.5)
    sq.move_to(corner + np.array([ix, iy, 0]) * 0.10)
    return sq


class PreguntaUNI22(Scene):
    def construct(self):
        self.intro()
        fig = self.construir_figura()
        self.idea_clave(fig)
        self.analizar_info_I(fig)
        self.analizar_info_II(fig)
        self.conclusion(fig)

    # ------------------------------------------------------------------ intro
    def intro(self):
        t1 = Text("Examen de Admisión UNI 2025", font_size=42, color=AZUL, weight=BOLD)
        t2 = Text("Pregunta N.º 22  ·  Suficiencia de datos", font_size=26, color=GREY_B)
        t2.next_to(t1, DOWN, buff=0.3)
        g = VGroup(t1, t2).move_to(ORIGIN)
        self.play(FadeIn(t1, shift=UP * 0.4))
        self.play(Write(t2))
        self.wait(0.9)
        self.play(FadeOut(g, shift=UP * 0.4))

    # --------------------------------------------------------------- figura
    def construir_figura(self):
        # Coordenadas en u: A(0,0) C(8,0) D(0,6) E(8,6) B(3,6)
        def P(x, y):
            return np.array([(x - 4) * S, (y - 3) * S, 0])

        A, C, D, E, B = P(0, 0), P(8, 0), P(0, 6), P(8, 6), P(3, 6)

        rect = Polygon(A, C, E, D, color=VINO, stroke_width=3)
        tri = Polygon(A, B, C, color=VINO, stroke_width=3)
        tri.set_fill(NARANJA, opacity=0.0)

        marks = VGroup(
            corner_mark(A, +1, +1), corner_mark(C, -1, +1),
            corner_mark(E, -1, -1), corner_mark(D, +1, -1),
        )

        lA = MathTex("A", font_size=30).next_to(A, DOWN + LEFT, buff=0.12)
        lC = MathTex("C", font_size=30).next_to(C, DOWN + RIGHT, buff=0.12)
        lD = MathTex("D", font_size=30).next_to(D, UP + LEFT, buff=0.12)
        lE = MathTex("E", font_size=30).next_to(E, UP + RIGHT, buff=0.12)
        lB = MathTex("B", font_size=30).next_to(B, UP, buff=0.12)
        base = MathTex(r"8\ \text{u}", font_size=28).next_to(Line(A, C), DOWN, buff=0.22)

        fig = VGroup(rect, tri, marks, lA, lC, lD, lE, lB, base)
        self.play(Create(rect), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(m) for m in marks], lag_ratio=0.2), run_time=0.8)
        self.play(Create(tri), run_time=1.0)
        self.play(*[FadeIn(m) for m in [lA, lC, lD, lE, lB]], FadeIn(base))
        self.wait(0.5)

        # guardamos puntos para reusarlos
        fig.pts = dict(A=A, C=C, D=D, E=E, B=B)
        return fig

    # ------------------------------------------------------------ idea clave
    def idea_clave(self, fig):
        self.play(fig.animate.scale(0.95).to_edge(LEFT, buff=0.8))
        A, C, B = fig.pts["A"], fig.pts["C"], fig.pts["B"]
        # recalculamos posiciones tras mover/escalar
        A = fig[0].get_vertices()[0]
        C = fig[0].get_vertices()[1]
        Bp = fig[1].get_vertices()[1]
        pie = np.array([Bp[0], A[1], 0])
        altura = DashedLine(Bp, pie, color=VERDE, stroke_width=4)
        h_lbl = MathTex("h", font_size=30, color=VERDE).next_to(altura, RIGHT, buff=0.12)

        idea = VGroup(
            Text("Idea clave", font_size=26, color=VERDE, weight=BOLD),
            Tex(r"$B$ está sobre $DE$, así que la altura\\del $\triangle ABC$ es la altura $h$ del\\rectángulo.", font_size=30),
            MathTex(r"[\triangle ABC]=\tfrac{1}{2}\cdot 8\cdot h = 4h", font_size=38, color=AZUL),
            Tex(r"$\Rightarrow$ basta conocer $h$.", font_size=32, color=NARANJA),
        ).arrange(DOWN, buff=0.45, aligned_edge=LEFT).to_edge(RIGHT, buff=0.7)

        self.play(Create(altura), FadeIn(h_lbl))
        self.play(FadeIn(idea[0], shift=UP * 0.2))
        self.play(Write(idea[1]))
        self.play(Write(idea[2]))
        self.play(FadeIn(idea[3], shift=UP * 0.2))
        self.wait(1.2)
        self.play(FadeOut(idea), FadeOut(altura), FadeOut(h_lbl))

    # --------------------------------------------------------- info I
    def analizar_info_I(self, fig):
        A = fig[0].get_vertices()[0]
        E = fig[0].get_vertices()[2]
        diag = Line(A, E, color=ROJO, stroke_width=4)
        diag_lbl = MathTex(r"10", font_size=32, color=YELLOW).move_to(
            (A + E) / 2 + np.array([0.40, 0.30, 0]))

        bloque = VGroup(
            Text("Información I", font_size=28, color=ROJO, weight=BOLD),
            MathTex(r"AE = 10\ \text{u}\ \ (\text{diagonal})", font_size=34),
            MathTex(r"8^{2} + h^{2} = 10^{2}", font_size=36),
            MathTex(r"h^{2} = 36 \;\Rightarrow\; h = 6", font_size=36, color=AZUL),
            MathTex(r"[\triangle ABC] = 4(6) = 24\ \text{u}^2", font_size=36, color=VERDE),
            Text("→ I es suficiente ✓", font_size=28, color=VERDE, weight=BOLD),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(RIGHT, buff=0.7)

        self.play(Create(diag), FadeIn(diag_lbl))
        self.play(FadeIn(bloque[0], shift=UP * 0.2))
        for m in bloque[1:]:
            self.play(FadeIn(m, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(bloque), FadeOut(diag), FadeOut(diag_lbl))

    # --------------------------------------------------------- info II
    def analizar_info_II(self, fig):
        rect = fig[0]
        flash = rect.copy().set_fill(NARANJA, opacity=0.25)

        bloque = VGroup(
            Text("Información II", font_size=28, color=ROJO, weight=BOLD),
            MathTex(r"[\,ADEC\,] = 48\ \text{u}^2", font_size=34),
            MathTex(r"8 \cdot h = 48", font_size=36),
            MathTex(r"h = 6", font_size=36, color=AZUL),
            MathTex(r"[\triangle ABC] = 4(6) = 24\ \text{u}^2", font_size=36, color=VERDE),
            Text("→ II es suficiente ✓", font_size=28, color=VERDE, weight=BOLD),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(RIGHT, buff=0.7)

        self.play(FadeIn(flash))
        self.play(FadeIn(bloque[0], shift=UP * 0.2))
        for m in bloque[1:]:
            self.play(FadeIn(m, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(bloque), FadeOut(flash))

    # --------------------------------------------------------- conclusion
    def conclusion(self, fig):
        self.play(FadeOut(fig))
        opts = VGroup(
            Text("Cada información, por separado,", font_size=34, color=WHITE),
            Text("es suficiente.", font_size=34, color=WHITE),
        ).arrange(DOWN, buff=0.2).shift(UP * 1.2)
        resp = MathTex(r"\textbf{Clave: D}", font_size=72, color=VERDE)
        caja = SurroundingRectangle(resp, color=VERDE, buff=0.35, corner_radius=0.15)
        firma = Text("Resuelto y animado con Manim", font_size=22, color=GREY_B)
        firma.to_edge(DOWN, buff=0.6)

        self.play(Write(opts))
        self.play(FadeIn(resp, scale=1.2), Create(caja))
        self.play(FadeIn(firma))
        self.wait(1.8)
