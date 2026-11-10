"""Criaturas y objetos animados por código, en el mismo estilo que los monigotes.

Cada criatura tiene:
  draw(ctx, t)    -> dibujo normal con partes que se mueven (tentáculos, cola, alas...)
  body(ctx, t)    -> contorno del cuerpo (para recortar el efecto rayos X)
  inside(ctx, t)  -> lo que se ve por dentro en modo rayos X
Coordenadas locales: (0, 0) = suelo, centro; hacia arriba es y negativo; ~600 px de alto.
"""
import math

import cairo

INK = (0.11, 0.11, 0.13)
GLOW = (0.45, 0.95, 1.0)


# ---------------------------------------------------------------- utilidades
def outline(ctx, fill, lw=11):
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(lw)
    ctx.stroke()


def ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def beat(t, bpm=80):
    """Latido: dos golpes rápidos por ciclo."""
    ph = (t * bpm / 60) % 1.0
    return max(math.exp(-((ph - 0.1) / 0.06) ** 2), 0.6 * math.exp(-((ph - 0.3) / 0.06) ** 2))


def eye(ctx, x, y, r, t, seed=0.0, look=(-0.35, 0.1)):
    blink = ((t + seed) % 3.3) < 0.13
    if blink:
        ctx.move_to(x - r, y)
        ctx.line_to(x + r, y)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(r * 0.25)
        ctx.stroke()
        return
    ctx.arc(x, y, r, 0, 2 * math.pi)
    outline(ctx, (1, 1, 1), r * 0.18)
    ctx.arc(x + look[0] * r * 0.9, y + look[1] * r, r * 0.45, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.arc(x + look[0] * r * 0.9 - r * 0.15, y + look[1] * r - r * 0.18, r * 0.14, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()


def smile(ctx, x, y, w, open_=0.0):
    ctx.set_source_rgb(*INK)
    if open_ > 0.1:
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 0.4 + open_)
        ctx.arc(0, 0, w, 0, math.pi)
        ctx.close_path()
        ctx.restore()
        ctx.fill()
    else:
        ctx.arc(x, y - w * 0.6, w, 0.4, math.pi - 0.4)
        ctx.set_line_width(w * 0.3)
        ctx.stroke()


def heart_shape(ctx, x, y, r, color=(0.95, 0.25, 0.32), glow=False):
    ctx.move_to(x, y + r * 0.85)
    ctx.curve_to(x - r * 1.3, y - r * 0.1, x - r * 0.55, y - r * 1.05, x, y - r * 0.35)
    ctx.curve_to(x + r * 0.55, y - r * 1.05, x + r * 1.3, y - r * 0.1, x, y + r * 0.85)
    ctx.close_path()
    if glow:
        ctx.set_source_rgba(*color, 0.35)
        ctx.set_line_width(r * 0.5)
        ctx.stroke_preserve()
    outline(ctx, color, max(r * 0.12, 4))


def tentacle(ctx, pts, w0, w1, color):
    n = len(pts) - 1
    for pass_, extra in ((0, 10), (1, 0)):
        for i in range(n):
            w = w0 + (w1 - w0) * i / n + extra
            ctx.set_source_rgb(*(INK if pass_ == 0 else color))
            ctx.set_line_width(w)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(*pts[i])
            ctx.line_to(*pts[i + 1])
            ctx.stroke()


def flow_line(ctx, pts, t, color, w=8):
    """Vaso sanguíneo / túnel con 'flujo' animado."""
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgba(*color, 0.45)
    ctx.set_line_width(w * 1.8)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*color)
    ctx.set_line_width(w)
    ctx.set_dash([18, 14], -t * 120)
    ctx.stroke()
    ctx.set_dash([])


def bones(ctx, x1, y1, x2, y2, w=14):
    ctx.set_source_rgb(0.95, 0.97, 1.0)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()
    for x, y in ((x1, y1), (x2, y2)):
        ctx.arc(x, y, w * 0.75, 0, 2 * math.pi)
        ctx.fill()


# ---------------------------------------------------------------- criaturas
class Creature:
    float_ = False  # flota (animales marinos, pájaros, planetas)
    color = (0.6, 0.6, 0.6)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)

    def body(self, ctx, t):
        ellipse(ctx, 0, -300, 200, 200)

    def inside(self, ctx, t):
        heart_shape(ctx, 0, -300, 50 * (1 + 0.18 * beat(t)), glow=True)


class Octopus(Creature):
    float_ = True
    color = (0.72, 0.42, 0.92)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-165, -300)
        ctx.curve_to(-200, -520, -100, -620, 0, -620)
        ctx.curve_to(100, -620, 200, -520, 165, -300)
        ctx.curve_to(120, -240, -120, -240, -165, -300)
        ctx.close_path()

    def draw(self, ctx, t):
        for k in range(8):
            x0 = -140 + k * 40
            spread = (k - 3.5) * 42
            pts = []
            for j in range(13):
                s = j / 12
                wave = 38 * math.sin(t * 3.2 + s * 4.5 + k * 0.9) * s
                pts.append((x0 + spread * s + wave, -270 + 250 * s - 40 * math.sin(s * math.pi) * (k % 2)))
            tentacle(ctx, pts, 46, 14, shade(self.color, 0.92 if k % 2 else 1.0))
            # ventosas
            for j in (4, 7, 10):
                ctx.arc(pts[j][0], pts[j][1], 5, 0, 2 * math.pi)
                ctx.set_source_rgb(1.0, 0.85, 0.95)
                ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        for sx in (-1, 1):  # manchas
            ellipse(ctx, sx * 90, -520, 18, 12)
            ctx.set_source_rgba(1, 1, 1, 0.25)
            ctx.fill()
        eye(ctx, -62, -400, 40, t, 0.2)
        eye(ctx, 62, -400, 40, t, 0.2)
        smile(ctx, 0, -320, 30, max(0, math.sin(t * 6)) * 0.6)

    def inside(self, ctx, t):
        b = beat(t, 70)
        # vasos de sangre azul desde los corazones
        flow_line(ctx, [(-75, -470), (-120, -400), (-140, -300)], t, (0.25, 0.55, 1.0))
        flow_line(ctx, [(75, -470), (120, -400), (140, -300)], t, (0.25, 0.55, 1.0))
        flow_line(ctx, [(0, -380), (0, -310), (0, -270)], t, (0.25, 0.55, 1.0))
        heart_shape(ctx, -75, -480, 34 * (1 + 0.22 * b), glow=True)
        heart_shape(ctx, 75, -480, 34 * (1 + 0.22 * beat(t + 0.15, 70)), glow=True)
        heart_shape(ctx, 0, -395, 48 * (1 + 0.22 * beat(t + 0.3, 70)), glow=True)
        # cerebro con forma de donut
        ellipse(ctx, 0, -560, 60, 26)
        ctx.set_source_rgba(1.0, 0.7, 0.85, 0.9)
        ctx.set_line_width(14)
        ctx.stroke()


class Fish(Creature):
    float_ = True
    color = (1.0, 0.6, 0.2)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-240, -330)
        ctx.curve_to(-180, -470, 120, -470, 190, -330)
        ctx.curve_to(120, -190, -180, -190, -240, -330)
        ctx.close_path()

    def draw(self, ctx, t):
        a = 0.35 * math.sin(t * 7)
        ctx.save()
        ctx.translate(180, -330)
        ctx.rotate(a)
        ctx.move_to(0, 0)
        ctx.line_to(140, -110)
        ctx.curve_to(110, 0, 110, 0, 140, 110)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 0.85))
        ctx.move_to(-60, -440)
        ctx.curve_to(-10, -560 - 15 * math.sin(t * 5), 70, -520, 90, -425)
        outline(ctx, shade(self.color, 0.85))
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(3):
            ctx.arc(-30 + k * 70, -330, 60, -0.9, 0.9)
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.set_line_width(8)
            ctx.stroke()
        eye(ctx, -150, -360, 30, t, 1.1)
        ctx.save()
        ctx.translate(-30 + 0, -260)
        ctx.rotate(0.4 * math.sin(t * 5))
        ctx.move_to(0, 0)
        ctx.line_to(-60, 60)
        ctx.line_to(20, 40)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 0.85), 8)
        smile(ctx, -205, -310, 16)

    def inside(self, ctx, t):
        bones(ctx, -170, -330, 170, -330, 12)
        for k in range(7):
            x = -110 + k * 40
            for sy in (-1, 1):
                ctx.move_to(x, -330)
                ctx.curve_to(x + 10, -330 + sy * 50, x + 20, -330 + sy * 70, x + 25, -330 + sy * 85)
                ctx.set_source_rgb(0.95, 0.97, 1)
                ctx.set_line_width(7)
                ctx.stroke()
        ctx.arc(-175, -345, 48, 0, 2 * math.pi)
        ctx.set_line_width(9)
        ctx.stroke()
        heart_shape(ctx, -120, -270, 22 * (1 + 0.25 * beat(t, 100)), glow=True)


class Whale(Creature):
    float_ = True
    color = (0.35, 0.55, 0.9)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-280, -300)
        ctx.curve_to(-280, -520, 120, -520, 210, -330)
        ctx.curve_to(240, -260, 200, -170, 60, -165)
        ctx.curve_to(-120, -160, -280, -190, -280, -300)
        ctx.close_path()

    def draw(self, ctx, t):
        a = 0.3 * math.sin(t * 3)
        ctx.save()
        ctx.translate(205, -300)
        ctx.rotate(-0.5 + a)
        ctx.move_to(0, 0)
        ctx.curve_to(60, -40, 130, -120, 150, -90)
        ctx.curve_to(120, -40, 120, -10, 160, 30)
        ctx.curve_to(110, 40, 50, 30, 0, 0)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 0.85))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.move_to(-270, -260)
        ctx.curve_to(-180, -170, 60, -170, 180, -240)
        ctx.curve_to(80, -175, -150, -165, -270, -260)
        ctx.set_source_rgb(0.85, 0.92, 1.0)
        ctx.fill()
        for k in range(4):
            ctx.move_to(-230 + k * 40, -240)
            ctx.line_to(-200 + k * 45, -205)
            ctx.set_source_rgb(*shade(self.color, 0.8))
            ctx.set_line_width(5)
            ctx.stroke()
        eye(ctx, -170, -330, 24, t, 0.7)
        smile(ctx, -220, -280, 20)
        # chorro de agua cada pocos segundos
        ph = (t * 0.6) % 1.0
        if ph < 0.55:
            h = math.sin(ph / 0.55 * math.pi)
            for k in range(7):
                ang = -math.pi / 2 + (k - 3) * 0.28
                d = 90 + 150 * h
                ctx.arc(-80 + math.cos(ang) * d * 0.6, -470 + math.sin(ang) * d, 13 + 5 * h, 0, 2 * math.pi)
                outline(ctx, (0.75, 0.9, 1.0), 5)

    def inside(self, ctx, t):
        b = beat(t, 40)
        flow_line(ctx, [(-40, -330), (-150, -300), (-240, -290)], t, (1.0, 0.35, 0.4), 10)
        flow_line(ctx, [(40, -330), (130, -290), (190, -300)], t, (1.0, 0.35, 0.4), 10)
        heart_shape(ctx, 0, -340, 80 * (1 + 0.15 * b), glow=True)
        for k in range(2):  # pulmones
            ellipse(ctx, -60 + k * 140, -410, 55, 30 * (1 + 0.1 * math.sin(t * 1.5)))
            ctx.set_source_rgba(1.0, 0.65, 0.75, 0.8)
            ctx.fill()


class Shark(Creature):
    float_ = True
    color = (0.55, 0.62, 0.72)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-300, -320)
        ctx.curve_to(-200, -450, 120, -440, 220, -340)
        ctx.curve_to(120, -230, -200, -220, -300, -320)
        ctx.close_path()

    def draw(self, ctx, t):
        a = 0.3 * math.sin(t * 6)
        ctx.save()
        ctx.translate(210, -340)
        ctx.rotate(a)
        ctx.move_to(0, 0)
        ctx.line_to(120, -150)
        ctx.line_to(80, 0)
        ctx.line_to(110, 90)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 0.85))
        ctx.move_to(-60, -425)
        ctx.line_to(20, -560 + 10 * math.sin(t * 4))
        ctx.line_to(70, -415)
        outline(ctx, shade(self.color, 0.85))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.move_to(-290, -310)
        ctx.curve_to(-200, -240, 100, -240, 200, -320)
        ctx.curve_to(100, -250, -200, -235, -290, -310)
        ctx.set_source_rgb(0.93, 0.95, 0.97)
        ctx.fill()
        for k in range(3):
            ctx.move_to(-130 + k * 25, -370)
            ctx.line_to(-140 + k * 25, -320)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        op = 0.5 + 0.5 * math.sin(t * 2.5)
        ctx.move_to(-270, -305)
        ctx.line_to(-190, -300 + 25 * op)
        ctx.line_to(-200, -300)
        ctx.close_path()
        ctx.set_source_rgb(0.8, 0.2, 0.3)
        ctx.fill()
        for k in range(5):
            x = -262 + k * 14
            ctx.move_to(x, -305)
            ctx.line_to(x + 7, -290)
            ctx.line_to(x + 14, -305)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
        eye(ctx, -200, -355, 18, t, 2.0, look=(-0.2, 0))

    def inside(self, ctx, t):
        bones(ctx, -230, -330, 200, -335, 11)
        for k in range(9):
            x = -150 + k * 38
            ctx.move_to(x, -330)
            ctx.line_to(x + 8, -380)
            ctx.move_to(x, -330)
            ctx.line_to(x + 8, -285)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(6)
            ctx.stroke()
        ctx.move_to(-280, -320)
        ctx.curve_to(-250, -270, -190, -270, -170, -300)
        ctx.set_line_width(12)
        ctx.stroke()
        heart_shape(ctx, -120, -290, 22 * (1 + 0.25 * beat(t, 60)), glow=True)


class Human(Creature):
    color = (0.98, 0.82, 0.68)

    def body(self, ctx, t):
        br = 1 + 0.02 * math.sin(t * 2)
        ctx.new_path()
        ctx.arc(0, -580, 95, 0, 2 * math.pi)
        ctx.new_sub_path()
        x0, y0, x1, y1, r = -130 * br, -470, 130 * br, -150, 60
        ctx.move_to(x0 + r, y0)
        ctx.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
        ctx.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
        ctx.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
        ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
        ctx.close_path()

    def draw(self, ctx, t):
        for sx in (-1, 1):  # piernas y brazos
            ctx.move_to(sx * 60, -170)
            ctx.line_to(sx * 70, 0)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(62)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke_preserve()
            ctx.set_source_rgb(0.3, 0.4, 0.7)
            ctx.set_line_width(46)
            ctx.stroke()
            sw = 0.15 * math.sin(t * 2 + sx)
            ctx.move_to(sx * 125, -430)
            ctx.line_to(sx * (175 + 30 * sw), -230)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(52)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*self.color)
            ctx.set_line_width(38)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        eye(ctx, -35, -595, 18, t, 0.4, look=(-0.4, 0))
        eye(ctx, 35, -595, 18, t, 0.4, look=(-0.4, 0))
        smile(ctx, 0, -540, 25)

    def inside(self, ctx, t):
        # cerebro con chispas
        for (a, b, c) in [(-30, -600, 42), (30, -605, 42), (-35, -570, 38), (35, -570, 38), (0, -590, 40)]:
            ctx.new_sub_path()
            ctx.arc(a, b, c, 0, 2 * math.pi)
        ctx.set_source_rgb(1.0, 0.68, 0.8)
        ctx.fill()
        for k in range(4):
            ph = (t * 1.7 + k * 0.37) % 1
            ctx.arc(-50 + k * 33, -600 + 20 * math.sin(k * 2), 7 * (1 - ph) + 2, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.5, 1 - ph)
            ctx.fill()
        # pulmones que respiran
        br = 1 + 0.12 * math.sin(t * 2)
        for sx in (-1, 1):
            ellipse(ctx, sx * 62, -370, 48 * br, 80 * br)
            ctx.set_source_rgba(1.0, 0.55, 0.65, 0.85)
            ctx.fill()
        flow_line(ctx, [(0, -470), (0, -420), (-62, -400)], t, (0.9, 0.95, 1), 6)
        heart_shape(ctx, 18, -345, 38 * (1 + 0.22 * beat(t)), glow=True)
        # estómago e intestinos
        ellipse(ctx, 30, -255, 52, 30)
        ctx.set_source_rgb(1.0, 0.75, 0.55)
        ctx.fill()
        ctx.move_to(-70, -215)
        for k in range(6):
            ctx.curve_to(-50 + k * 25, -235 + (k % 2) * 50, -40 + k * 25, -180, -30 + k * 25, -210 + (k % 2) * 20)
        ctx.set_source_rgb(1.0, 0.65, 0.6)
        ctx.set_line_width(14)
        ctx.stroke()


class Earth(Creature):
    float_ = True
    color = (0.3, 0.6, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -330, 235, 0, 2 * math.pi)

    def draw(self, ctx, t):
        self.body(ctx, t)
        ctx.set_source_rgb(*self.color)
        ctx.fill()
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        off = (t * 60) % 700
        for base in (-off, 700 - off):
            for (a, b, rx, ry) in [(-120, -420, 90, 60), (60, -300, 120, 80), (-60, -200, 70, 45),
                                   (230, -440, 80, 50), (330, -250, 90, 60)]:
                ellipse(ctx, base + a, b, rx, ry)
                ctx.set_source_rgb(0.3, 0.78, 0.4)
                ctx.fill()
        for k in range(3):
            cx = ((t * 90 + k * 230) % 700) - 350
            ellipse(ctx, cx, -470 + k * 120, 70, 18)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.fill()
        ctx.restore()
        self.body(ctx, t)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(11)
        ctx.stroke()
        eye(ctx, -70, -360, 30, t, 0.9)
        eye(ctx, 70, -360, 30, t, 0.9)
        smile(ctx, 0, -270, 32)

    def inside(self, ctx, t):
        p = 1 + 0.03 * math.sin(t * 4)
        for r, c in [(230, (0.55, 0.38, 0.22)), (200, (0.95, 0.45, 0.15)), (120, (1.0, 0.7, 0.15)),
                     (60 * p, (1.0, 0.95, 0.55))]:
            ctx.arc(0, -330, r, 0, 2 * math.pi)
            ctx.set_source_rgb(*c)
            ctx.fill()
        ctx.arc(0, -330, 75 * p, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.8, 0.35)
        ctx.fill()


class Volcano(Creature):
    color = (0.55, 0.38, 0.26)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-300, 0)
        ctx.line_to(-90, -480)
        ctx.line_to(90, -480)
        ctx.line_to(300, 0)
        ctx.close_path()

    def draw(self, ctx, t):
        # humo
        for k in range(5):
            ph = (t * 0.5 + k / 5) % 1
            ellipse(ctx, 30 * math.sin(k * 2 + t), -520 - ph * 380, 50 + 60 * ph, 40 + 50 * ph)
            ctx.set_source_rgba(0.5, 0.5, 0.55, 0.6 * (1 - ph))
            ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.move_to(-90, -480)
        ctx.line_to(-60, -400)
        ctx.line_to(-30, -440)
        ctx.line_to(10, -380)
        ctx.line_to(40, -430)
        ctx.line_to(70, -390)
        ctx.line_to(90, -480)
        ctx.close_path()
        outline(ctx, (1.0, 0.45, 0.1), 8)
        # lava que salta
        for k in range(7):
            ph = (t * 0.9 + k / 7) % 1
            vx = (k - 3) * 55
            x = vx * ph * 2
            y = -480 - 520 * ph + 600 * ph * ph
            ctx.arc(x, y, 18 - 6 * ph, 0, 2 * math.pi)
            outline(ctx, (1.0, 0.5 + 0.3 * (1 - ph), 0.1), 5)
        eye(ctx, -55, -260, 26, t, 1.5)
        eye(ctx, 55, -260, 26, t, 1.5)
        smile(ctx, 0, -185, 28, 0.5 + 0.3 * math.sin(t * 5))

    def inside(self, ctx, t):
        ellipse(ctx, 0, -90, 170, 60 * (1 + 0.06 * math.sin(t * 3)))
        ctx.set_source_rgb(1.0, 0.45, 0.1)
        ctx.fill()
        flow_line(ctx, [(0, -110), (-15, -280), (10, -470)], t * 1.5, (1.0, 0.6, 0.15), 30)
        for k in range(6):
            ph = (t * 0.8 + k / 6) % 1
            ctx.arc(10 * math.sin(k * 3), -100 - 370 * ph, 10, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.95, 0.5, 1 - ph)
            ctx.fill()


class Pyramid(Creature):
    color = (0.96, 0.8, 0.45)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-320, 0)
        ctx.line_to(0, -560)
        ctx.line_to(320, 0)
        ctx.close_path()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        ctx.set_source_rgba(0.6, 0.45, 0.2, 0.5)
        ctx.set_line_width(4)
        for k in range(1, 10):
            y = -k * 56
            ctx.move_to(-320, y)
            ctx.line_to(320, y)
            ctx.stroke()
            for j in range(-6, 7):
                x = j * 60 + (k % 2) * 30
                ctx.move_to(x, y)
                ctx.line_to(x, y + 56)
                ctx.stroke()
        ctx.move_to(0, -560)
        ctx.line_to(320, 0)
        ctx.line_to(60, 0)
        ctx.close_path()
        ctx.set_source_rgba(0, 0, 0, 0.12)
        ctx.fill()
        ctx.restore()
        ctx.rectangle(-30, -80, 60, 80)
        outline(ctx, (0.35, 0.25, 0.15), 8)

    def inside(self, ctx, t):
        path = [(0, -40), (-40, -120), (-120, -120), (-120, -60)]
        flow_line(ctx, path, t, (1.0, 0.85, 0.4), 12)
        flow_line(ctx, [(-40, -120), (20, -200), (90, -330)], t, (1.0, 0.85, 0.4), 18)
        flow_line(ctx, [(-120, -120), (-60, -200), (-30, -220)], t, (1.0, 0.85, 0.4), 10)
        for (x, y, w, h, name) in [(60, -360, 90, 55, "rey"), (-70, -240, 70, 45, "reina"), (-150, -90, 70, 40, "")]:
            ctx.rectangle(x, y, w, h)
            outline(ctx, (1.0, 0.92, 0.6), 6)
        ctx.rectangle(85, -340, 40, 22)  # sarcófago
        ctx.set_source_rgb(1.0, 0.75, 0.2)
        ctx.fill()
        ph = (t * 0.35) % 1  # explorador con linterna recorriendo el túnel
        x, y = -40 + 130 * ph, -120 - 210 * ph
        ctx.arc(x, y, 30, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.7, 0.35)
        ctx.fill()
        ctx.arc(x, y, 9, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 0.8)
        ctx.fill()


class Bird(Creature):
    float_ = True
    color = (0.35, 0.75, 0.95)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -340, 150, 120)

    def draw(self, ctx, t):
        flap = math.sin(t * 9)
        ctx.move_to(170, -360)
        ctx.line_to(290, -420)
        ctx.line_to(280, -320)
        ctx.close_path()
        outline(ctx, shade(self.color, 0.85))
        self.body(ctx, t)
        outline(ctx, self.color)
        ellipse(ctx, -20, -300, 90, 60)
        ctx.set_source_rgb(0.9, 0.97, 1.0)
        ctx.fill()
        ctx.save()
        ctx.translate(40, -380)
        ctx.rotate(-0.9 * flap)
        ctx.move_to(0, 0)
        ctx.curve_to(80, -60, 200, -60, 230, -10)
        ctx.curve_to(150, 10, 80, 30, 0, 0)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 0.85))
        ctx.move_to(-150, -370)
        ctx.line_to(-230, -345)
        ctx.line_to(-150, -320)
        ctx.close_path()
        outline(ctx, (1.0, 0.7, 0.15), 8)
        eye(ctx, -85, -385, 26, t, 0.3)

    def inside(self, ctx, t):
        bones(ctx, -90, -330, 110, -340, 10)
        ctx.arc(-95, -380, 45, 0, 2 * math.pi)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(8)
        ctx.stroke()
        heart_shape(ctx, -20, -320, 26 * (1 + 0.3 * beat(t, 200)), glow=True)
        for k in range(3):  # sacos de aire
            ellipse(ctx, 40 + k * 30, -290, 20, 14 * (1 + 0.2 * math.sin(t * 6 + k)))
            ctx.set_source_rgba(0.8, 0.95, 1, 0.8)
            ctx.fill()


class Cat(Creature):
    color = (0.98, 0.65, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -200, 160, 190)
        ctx.new_sub_path()
        ctx.arc(-20, -470, 125, 0, 2 * math.pi)

    def draw(self, ctx, t):
        sw = math.sin(t * 2.5)
        ctx.move_to(130, -60)
        ctx.curve_to(260, -80, 230 + 60 * sw, -280, 200 + 80 * sw, -380)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(56)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(36)
        ctx.stroke()
        for sx in (-1, 1):
            ctx.move_to(-20 + sx * 40, -560)
            ctx.line_to(-20 + sx * 115, -650 + 8 * math.sin(t * 6 + sx))
            ctx.line_to(-20 + sx * 115, -520)
            ctx.close_path()
            outline(ctx, self.color)
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(3):
            ctx.move_to(-20 + (k - 1) * 40, -590)
            ctx.line_to(-20 + (k - 1) * 30, -560)
            ctx.set_source_rgb(*shade(self.color, 0.75))
            ctx.set_line_width(10)
            ctx.stroke()
        eye(ctx, -65, -480, 26, t, 2.2)
        eye(ctx, 25, -480, 26, t, 2.2)
        ctx.move_to(-28, -430)
        ctx.line_to(-12, -430)
        ctx.line_to(-20, -420)
        ctx.close_path()
        ctx.set_source_rgb(1.0, 0.5, 0.6)
        ctx.fill()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        for sy in (-8, 4):
            for sx in (-1, 1):
                ctx.move_to(-20 + sx * 30, -425 + sy)
                ctx.line_to(-20 + sx * 110, -432 + sy * 2)
        ctx.stroke()

    def inside(self, ctx, t):
        ctx.arc(-20, -470, 95, 0, 2 * math.pi)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(9)
        ctx.stroke()
        bones(ctx, 0, -360, 20, -60, 12)
        for k in range(6):
            y = -330 + k * 38
            for sx in (-1, 1):
                ctx.move_to(5, y)
                ctx.curve_to(sx * 60, y - 10, sx * 100, y + 10, sx * 110, y + 35)
                ctx.set_line_width(7)
                ctx.stroke()
        heart_shape(ctx, -30, -250, 30 * (1 + 0.25 * beat(t, 140)), glow=True)
        for k in range(3):  # ronroneo
            ph = (t * 1.5 + k / 3) % 1
            ctx.arc(-20, -420, 30 + 90 * ph, -2.4, -0.7)
            ctx.set_source_rgba(1, 1, 0.6, 1 - ph)
            ctx.set_line_width(6)
            ctx.stroke()


class Dinosaur(Creature):
    color = (0.45, 0.8, 0.4)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-60, -380)
        ctx.curve_to(-40, -520, 120, -520, 160, -380)
        ctx.curve_to(200, -260, 120, -170, 20, -170)
        ctx.curve_to(-80, -170, -100, -280, -60, -380)
        ctx.close_path()
        ctx.new_sub_path()
        ellipse(ctx, -120, -560, 120, 85)

    def draw(self, ctx, t):
        sw = math.sin(t * 2.2)
        ctx.move_to(150, -260)
        ctx.curve_to(260, -250, 320, -200 + 30 * sw, 360, -140 + 40 * sw)
        ctx.curve_to(300, -150, 240, -170, 120, -190)
        outline(ctx, shade(self.color, 0.9))
        step = math.sin(t * 4)
        for sx, ph in ((-1, 0), (1, math.pi)):
            ctx.move_to(40 + sx * 50, -200)
            ctx.line_to(40 + sx * 55 + 15 * math.sin(t * 4 + ph), -10)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(70)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*shade(self.color, 0.9))
            ctx.set_line_width(54)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(5):  # placas del lomo
            x = -20 + k * 40
            ctx.move_to(x - 15, -470 + k * 10)
            ctx.line_to(x, -510 + k * 10)
            ctx.line_to(x + 15, -470 + k * 10)
            outline(ctx, (1.0, 0.6, 0.2), 6)
        ctx.move_to(-40, -340)
        ctx.line_to(-110, -330 + 20 * step)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(26)
        ctx.stroke()
        roar = max(0, math.sin(t * 1.6)) ** 3
        ctx.move_to(-235, -540)
        ctx.line_to(-110, -540 + 70 * roar)
        ctx.line_to(-235, -520 + 40 * roar)
        ctx.close_path()
        ctx.set_source_rgb(0.75, 0.2, 0.25)
        ctx.fill()
        eye(ctx, -110, -600, 24, t, 1.3)

    def inside(self, ctx, t):
        ctx.arc(-120, -560, 80, 0, 2 * math.pi)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(9)
        ctx.stroke()
        bones(ctx, -60, -480, 140, -300, 13)
        for k in range(6):
            x, y = -40 + k * 30, -450 + k * 28
            ctx.move_to(x, y)
            ctx.curve_to(x - 10, y + 60, x + 10, y + 120, x + 30, y + 150)
            ctx.set_line_width(8)
            ctx.stroke()
        heart_shape(ctx, 20, -330, 40 * (1 + 0.2 * beat(t, 50)), glow=True)


def shade(c, f):
    return tuple(min(max(v * f, 0), 1) for v in c)


CREATURES = {
    "octopus": Octopus(), "fish": Fish(), "whale": Whale(), "shark": Shark(), "human": Human(),
    "earth": Earth(), "volcano": Volcano(), "pyramid": Pyramid(), "bird": Bird(), "cat": Cat(),
    "dinosaur": Dinosaur(),
}


# partes de cada criatura (coordenadas locales) desde donde sale la lupa del zoom
PARTS = {
    "human": {"brain": (0, -590), "heart": (18, -345), "lungs": (-62, -370), "stomach": (30, -255),
              "intestines": (0, -200), "eye": (-35, -595), "body": (0, -350)},
    "octopus": {"hearts": (0, -440), "heart": (0, -440), "brain": (0, -560), "tentacles": (60, -120), "body": (0, -430)},
    "fish": {"heart": (-120, -270), "body": (0, -330), "gills": (-150, -320)},
    "whale": {"heart": (0, -340), "lungs": (-60, -410), "body": (0, -330)},
    "shark": {"heart": (-120, -290), "teeth": (-230, -300), "body": (0, -330)},
    "earth": {"core": (0, -330), "surface": (100, -480), "body": (0, -330)},
    "volcano": {"magma": (0, -90), "crater": (0, -480), "body": (0, -250)},
    "pyramid": {"chamber": (105, -330), "tunnel": (20, -200), "body": (0, -250)},
    "bird": {"heart": (-20, -320), "wing": (120, -420), "body": (0, -340)},
    "cat": {"heart": (-30, -250), "brain": (-20, -480), "body": (0, -250)},
    "dinosaur": {"heart": (20, -330), "teeth": (-200, -540), "body": (40, -340)},
}


_FIT = {}


def fit_scale(name, scale, max_h=720, max_w=760):
    """Reduce los modelos muy altos o anchos para que no tapen textos ni al narrador."""
    if name not in _FIT:
        rec = cairo.RecordingSurface(cairo.CONTENT_COLOR_ALPHA, None)
        c = cairo.Context(rec)
        CREATURES[name].draw(c, 0.5)  # tamaño real de lo que se dibuja (cuello, antenas, mástil...)
        x, y, w, h = rec.ink_extents()
        h, w = max(-y, 1), max(w, 1)
        _FIT[name] = min(1.0, max_h / h, max_w / w)
    return scale * _FIT[name]


def part_point(name, part, t, cx, base, scale):
    """Posición en pantalla de una parte de la criatura (para el cono de la lupa)."""
    scale = fit_scale(name, scale)
    cr = CREATURES[name]
    pts = PARTS.get(name, {})
    x, y = pts.get(part) or pts.get("body") or (0, -300)
    bob = -18 * math.sin(t * 2.2) - 40 if cr.float_ else 0
    return cx + x * scale, base + bob + y * scale


def draw_creature(ctx, name, t, cx, base, scale, xray_t=None, shake=0.0):
    """Dibuja la criatura; si xray_t no es None, a partir de ese segundo se ve por dentro."""
    cr = CREATURES[name]
    scale = fit_scale(name, scale)
    k = _pop((t - 0.05) / 0.45)
    if k <= 0:
        return
    bob = -18 * math.sin(t * 2.2) - 40 if cr.float_ else 0
    squash = 1 + 0.03 * math.sin(t * 3.5)
    ctx.save()
    ctx.translate(cx + shake * 10 * math.sin(t * 70), base + bob)
    ctx.scale(scale * k / squash, scale * k * squash)

    cr.draw(ctx, t)
    if xray_t is not None and t > xray_t:
        x = min((t - xray_t) / 0.5, 1.0)
        ctx.save()
        cr.body(ctx, t)
        ctx.clip()
        x1, y1, x2, y2 = ctx.clip_extents()
        scan = y1 + (y2 - y1) * x
        ctx.rectangle(x1, y1, x2 - x1, scan - y1)  # el escáner baja revelando el interior
        ctx.clip()
        ctx.set_source_rgba(0.04, 0.1, 0.25, 0.9)
        ctx.paint()
        ctx.set_source_rgba(*GLOW, 0.12)  # rejilla de rayos X
        ctx.set_line_width(2)
        for gy in range(int(y1), int(y2), 28):
            ctx.move_to(x1, gy)
            ctx.line_to(x2, gy)
        ctx.stroke()
        cr.inside(ctx, t)
        ctx.restore()
        cr.body(ctx, t)
        ctx.set_source_rgba(*GLOW, 0.9 * x)
        ctx.set_line_width(12)
        ctx.stroke()
        if x < 1:
            ctx.save()
            cr.body(ctx, t)
            ctx.clip()
            ctx.rectangle(x1, scan - 6, x2 - x1, 12)
            ctx.set_source_rgba(*GLOW, 0.95)
            ctx.fill()
            ctx.restore()
    ctx.restore()


def _pop(x, k=1.9):
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2
