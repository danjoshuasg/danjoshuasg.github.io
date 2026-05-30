"""
Resolución animada de un problema estilo Examen de Admisión UNI (Álgebra / Funciones).

Problema:
    Sea f(x) = x^2 - 4x + 3. La gráfica de f corta a los ejes coordenados
    en tres puntos. Calcule el área de la región triangular que determinan.

Render:
    manim -qh manim_uni/uni2025.py SolucionUNI
"""
from manim import *


# Paleta
AZUL = "#2E86DE"
VERDE = "#27AE60"
NARANJA = "#E67E22"
ROJO = "#E74C3C"


class SolucionUNI(Scene):
    def construct(self):
        self.intro()
        self.enunciado()
        self.factorizar()
        self.grafica_y_area()
        self.cierre()

    # ----------------------------------------------------------------- intro
    def intro(self):
        titulo = Text("Examen de Admisión UNI", font_size=44, color=AZUL, weight=BOLD)
        sub = Text("Estilo 2025  ·  Álgebra y Funciones", font_size=26, color=GREY_B)
        sub.next_to(titulo, DOWN, buff=0.3)
        g = VGroup(titulo, sub).move_to(ORIGIN)
        self.play(FadeIn(titulo, shift=UP * 0.5))
        self.play(Write(sub))
        self.wait(0.8)
        self.play(FadeOut(g, shift=UP * 0.5))

    # ------------------------------------------------------------- enunciado
    def enunciado(self):
        tag = Text("Problema", font_size=28, color=NARANJA, weight=BOLD).to_edge(UP, buff=0.6)
        func = MathTex(r"f(x) = x^{2} - 4x + 3", font_size=52)
        func.next_to(tag, DOWN, buff=0.6)
        texto = Tex(
            r"La gráfica de $f$ corta a los ejes coordenados en\\"
            r"tres puntos. Calcule el \textbf{área} de la región\\"
            r"triangular que determinan dichos puntos.",
            font_size=36,
            tex_environment="center",
        )
        texto.next_to(func, DOWN, buff=0.6)

        self.play(FadeIn(tag, shift=DOWN * 0.3))
        self.play(Write(func))
        self.play(FadeIn(texto, shift=UP * 0.3))
        self.wait(1.2)
        self.play(func.animate.scale(0.8).to_corner(UL).shift(DOWN * 0.4 + RIGHT * 0.3),
                  FadeOut(tag), FadeOut(texto))
        self.func_corner = func

    # ------------------------------------------------------------ factorizar
    def factorizar(self):
        paso1 = Text("1)  Intersección con el eje X:  f(x) = 0", font_size=30, color=VERDE)
        paso1.to_edge(UP, buff=1.4).to_edge(LEFT, buff=0.8)

        eq1 = MathTex(r"x^{2} - 4x + 3 = 0", font_size=44)
        eq2 = MathTex(r"(x - 1)(x - 3) = 0", font_size=44)
        eq3 = MathTex(r"x = 1 \quad \vee \quad x = 3", font_size=44, color=AZUL)
        cadena = VGroup(eq1, eq2, eq3).arrange(DOWN, buff=0.55).next_to(paso1, DOWN, buff=0.6)
        cadena.to_edge(LEFT, buff=1.2)

        self.play(FadeIn(paso1, shift=RIGHT * 0.3))
        self.play(Write(eq1))
        self.play(TransformMatchingShapes(eq1.copy(), eq2))
        self.play(Write(eq3))
        self.wait(0.6)

        paso2 = Text("2)  Intersección con el eje Y:  x = 0", font_size=30, color=VERDE)
        paso2.next_to(cadena, DOWN, buff=0.7).to_edge(LEFT, buff=0.8)
        eqy = MathTex(r"f(0) = 3 \;\Rightarrow\; (0,\,3)", font_size=44, color=NARANJA)
        eqy.next_to(paso2, DOWN, buff=0.5).to_edge(LEFT, buff=1.2)

        self.play(FadeIn(paso2, shift=RIGHT * 0.3))
        self.play(Write(eqy))
        self.wait(0.6)

        puntos = MathTex(r"A(1,0)\quad B(3,0)\quad C(0,3)", font_size=40, color=WHITE)
        puntos.next_to(eqy, DOWN, buff=0.7).to_edge(LEFT, buff=1.0)
        caja = SurroundingRectangle(puntos, color=AZUL, buff=0.2, corner_radius=0.1)
        self.play(Write(puntos), Create(caja))
        self.wait(1.0)

        self.play(
            *[FadeOut(m) for m in [paso1, cadena, paso2, eqy, puntos, caja, self.func_corner]]
        )

    # --------------------------------------------------------- grafica y area
    def grafica_y_area(self):
        titulo = Text("3)  Construimos la región y calculamos el área",
                      font_size=28, color=VERDE).to_edge(UP, buff=0.5)
        self.play(FadeIn(titulo, shift=DOWN * 0.3))

        axes = Axes(
            x_range=[-1, 5, 1],
            y_range=[-2, 4, 1],
            x_length=6.5,
            y_length=5.2,
            axis_config={"include_tip": True, "include_numbers": True, "font_size": 22},
        ).to_edge(LEFT, buff=0.7).shift(DOWN * 0.3)

        graph = axes.plot(lambda x: x**2 - 4 * x + 3, x_range=[-0.4, 4.4], color=AZUL)
        graph_label = MathTex("f", color=AZUL, font_size=34).next_to(
            axes.c2p(4.3, graph.underlying_function(4.3)), RIGHT, buff=0.1)

        self.play(Create(axes))
        self.play(Create(graph), FadeIn(graph_label))
        self.wait(0.3)

        # Puntos de corte
        A = axes.c2p(1, 0)
        B = axes.c2p(3, 0)
        C = axes.c2p(0, 3)
        dA = Dot(A, color=AZUL); dB = Dot(B, color=AZUL); dC = Dot(C, color=NARANJA)
        lA = MathTex("A(1,0)", font_size=26).next_to(dA, DOWN, buff=0.15)
        lB = MathTex("B(3,0)", font_size=26).next_to(dB, DOWN + RIGHT, buff=0.15)
        lC = MathTex("C(0,3)", font_size=26).next_to(dC, LEFT, buff=0.15)
        self.play(LaggedStart(GrowFromCenter(dA), GrowFromCenter(dB), GrowFromCenter(dC), lag_ratio=0.4))
        self.play(FadeIn(lA), FadeIn(lB), FadeIn(lC))
        self.wait(0.3)

        # Triángulo
        tri = Polygon(A, B, C, color=VERDE, fill_opacity=0.35, stroke_color=VERDE)
        self.play(Create(tri))
        self.wait(0.5)

        # Cálculo del área (panel derecho)
        panel = VGroup(
            Text("Área del triángulo", font_size=26, color=VERDE, weight=BOLD),
            MathTex(r"\text{base } \overline{AB} = 3 - 1 = 2", font_size=34),
            MathTex(r"\text{altura} = y_C = 3", font_size=34),
            MathTex(r"S = \tfrac{1}{2}\,(\text{base})(\text{altura})", font_size=34),
            MathTex(r"S = \tfrac{1}{2}\,(2)(3)", font_size=34),
            MathTex(r"\boxed{\,S = 3\ \text{u}^2\,}", font_size=44, color=ROJO),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT).to_edge(RIGHT, buff=0.6).shift(DOWN * 0.2)

        for m in panel:
            self.play(FadeIn(m, shift=UP * 0.2), run_time=0.6)
        self.wait(1.2)

        self.grafica_group = VGroup(titulo, axes, graph, graph_label, dA, dB, dC,
                                    lA, lB, lC, tri, panel)

    # ----------------------------------------------------------------- cierre
    def cierre(self):
        self.play(FadeOut(self.grafica_group))
        resp = VGroup(
            Text("Respuesta", font_size=30, color=GREY_B),
            MathTex(r"S = 3\ \text{u}^2", font_size=72, color=VERDE),
            Text("Hecho con Manim · estilo UNI", font_size=22, color=GREY_B),
        ).arrange(DOWN, buff=0.6).move_to(ORIGIN)
        self.play(Write(resp[0]))
        self.play(FadeIn(resp[1], scale=1.2))
        self.play(FadeIn(resp[2]))
        self.wait(1.5)
