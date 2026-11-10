"""Objetos y cosas grandes animadas (con cara simpática algunas) y su interior en rayos X."""
import math
import random

import cairo

from src.creatures import INK, Creature, beat, ellipse, eye, flow_line, heart_shape, outline, shade, smile


def poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def rrect(ctx, x0, y0, x1, y1, r):
    ctx.new_sub_path()
    ctx.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
    ctx.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
    ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def face(ctx, x, y, s, t, seed=0.3, open_=0.0):
    eye(ctx, x - 40 * s, y, 20 * s, t, seed, look=(-0.3, 0.1))
    eye(ctx, x + 40 * s, y, 20 * s, t, seed, look=(-0.3, 0.1))
    smile(ctx, x, y + 50 * s, 24 * s, open_)


def gear(ctx, x, y, r, a, color=(0.75, 0.8, 0.9)):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(a)
    for k in range(8):
        ctx.rotate(math.pi / 4)
        ctx.rectangle(r * 0.8, -r * 0.18, r * 0.4, r * 0.36)
    ctx.new_sub_path()
    ctx.arc(0, 0, r * 0.85, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*color)
    ctx.fill()
    ctx.arc(x, y, r * 0.3, 0, 2 * math.pi)
    ctx.set_source_rgb(0.1, 0.15, 0.3)
    ctx.fill()


def glow(ctx, x, y, r, color, a=0.4):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *color, a)
    g.add_color_stop_rgba(1, *color, 0)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


def bubbles_up(ctx, t, x, y0, y1, n, color, size=8, spread=30):
    for k in range(n):
        ph = (t * 0.8 + k / n) % 1
        ctx.arc(x + spread * math.sin(k * 2.3 + t), y0 + (y1 - y0) * ph, size * (1 - ph * 0.5), 0, 2 * math.pi)
        ctx.set_source_rgba(*color, 1 - ph)
        ctx.fill()


class Thing(Creature):
    color = (0.7, 0.7, 0.75)


# ---------------------------------------------------------------- espacio
class Rocket(Thing):
    float_ = True
    color = (0.93, 0.94, 0.97)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(0, -720)
        ctx.curve_to(110, -620, 110, -350, 90, -200)
        ctx.line_to(-90, -200)
        ctx.curve_to(-110, -350, -110, -620, 0, -720)
        ctx.close_path()

    def draw(self, ctx, t):
        f = 1 + 0.2 * math.sin(t * 30)
        for k, (c, s) in enumerate((((1.0, 0.5, 0.1), 1.0), ((1.0, 0.85, 0.3), 0.6))):
            ctx.move_to(-60 * s, -200)
            ctx.curve_to(-50 * s, -100, -20 * s, -40 * f, 0, 30 * f * s - 40 * k)
            ctx.curve_to(20 * s, -40 * f, 50 * s, -100, 60 * s, -200)
            ctx.close_path()
            ctx.set_source_rgb(*c)
            ctx.fill()
        for sx in (-1, 1):
            poly(ctx, [(sx * 80, -330), (sx * 170, -200), (sx * 160, -150), (sx * 90, -210)])
            outline(ctx, (0.9, 0.25, 0.25))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.move_to(-55, -660)
        ctx.curve_to(-20, -700, 20, -700, 55, -660)
        ctx.close_path()
        outline(ctx, (0.9, 0.25, 0.25), 8)
        ctx.arc(0, -500, 55, 0, 2 * math.pi)
        outline(ctx, (0.45, 0.75, 1.0), 10)
        ctx.arc(-15, -515, 15, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.fill()

    def inside(self, ctx, t):
        for (y, c) in ((-420, (0.4, 0.7, 1.0)), (-300, (1.0, 0.75, 0.3))):
            rrect(ctx, -55, y - 50, 55, y + 50, 20)
            ctx.set_source_rgb(*c)
            ctx.fill()
        flow_line(ctx, [(0, -420), (0, -300), (0, -210)], t * 2, (1, 0.6, 0.2), 12)
        ctx.arc(0, -560, 30, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.85, 0.7)
        ctx.fill()


class UFO(Thing):
    float_ = True
    color = (0.75, 0.78, 0.85)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -450, 260, 70)
        ctx.new_sub_path()
        ctx.arc(0, -480, 120, math.pi, 2 * math.pi)
        ctx.close_path()

    def draw(self, ctx, t):
        a = 0.25 + 0.15 * math.sin(t * 3)
        poly(ctx, [(-90, -420), (90, -420), (220, 0), (-220, 0)])
        ctx.set_source_rgba(0.6, 1.0, 0.6, a)
        ctx.fill()
        ctx.arc(0, -480, 120, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.set_source_rgba(0.6, 0.9, 1.0, 0.8)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(10)
        ctx.stroke()
        ellipse(ctx, 0, -450, 260, 70)
        outline(ctx, self.color)
        for k in range(7):
            ctx.arc(-180 + k * 60, -440, 14, 0, 2 * math.pi)
            on = (int(t * 6) + k) % 3 == 0
            ctx.set_source_rgb(*((1, 0.9, 0.3) if on else (0.5, 0.5, 0.55)))
            ctx.fill()

    def inside(self, ctx, t):
        ctx.arc(0, -510, 45, 0, 2 * math.pi)
        ctx.set_source_rgb(0.55, 0.9, 0.45)
        ctx.fill()
        for sx in (-1, 1):
            ellipse(ctx, sx * 18, -515, 10, 16)
            ctx.set_source_rgb(*INK)
            ctx.fill()
        gear(ctx, -120, -450, 30, t * 3)
        gear(ctx, 120, -450, 30, -t * 3)


class Sun(Thing):
    float_ = True
    color = (1.0, 0.82, 0.2)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -380, 210, 0, 2 * math.pi)

    def draw(self, ctx, t):
        glow(ctx, 0, -380, 420, (1, 0.8, 0.3), 0.45)
        ctx.save()
        ctx.translate(0, -380)
        ctx.rotate(t * 0.4)
        for k in range(14):
            ctx.rotate(math.pi / 7)
            poly(ctx, [(220, -30), (320 + 20 * math.sin(t * 4 + k), 0), (220, 30)])
            ctx.set_source_rgb(1.0, 0.65, 0.15)
            ctx.fill()
        ctx.restore()
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -400, 1.3, t, 0.5)

    def inside(self, ctx, t):
        p = 1 + 0.04 * math.sin(t * 5)
        for r, c in ((200, (1.0, 0.55, 0.15)), (140, (1.0, 0.75, 0.2)), (75 * p, (1.0, 1.0, 0.7))):
            ctx.arc(0, -380, r, 0, 2 * math.pi)
            ctx.set_source_rgb(*c)
            ctx.fill()
        for k in range(6):  # fusión: núcleos que chocan y brillan
            a = t * 2 + k
            ctx.arc(math.cos(a) * 50, -380 + math.sin(a) * 50, 12, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.4, 0.3)
            ctx.fill()


class Moon(Thing):
    float_ = True
    color = (0.88, 0.88, 0.85)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -380, 210, 0, 2 * math.pi)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for (x, y, r) in ((-110, -460, 40), (90, -280, 55), (120, -490, 28), (-90, -280, 30)):
            ctx.arc(x, y, r, 0, 2 * math.pi)
            outline(ctx, shade(self.color, 0.85), 5)
        face(ctx, 0, -400, 1.2, t, 1.1)

    def inside(self, ctx, t):
        for r, c in ((200, (0.6, 0.6, 0.6)), (110, (0.8, 0.45, 0.2)), (50, (1.0, 0.75, 0.3))):
            ctx.arc(0, -380, r, 0, 2 * math.pi)
            ctx.set_source_rgb(*c)
            ctx.fill()


class Saturn(Thing):
    float_ = True
    color = (0.95, 0.78, 0.5)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -380, 170, 0, 2 * math.pi)

    def _ring(self, ctx, back):
        ctx.save()
        ctx.translate(0, -380)
        ctx.rotate(-0.3)
        ctx.scale(1, 0.25)
        ctx.arc(0, 0, 320, math.pi if back else 0, 2 * math.pi if back else math.pi)
        ctx.restore()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(44)
        ctx.stroke_preserve()
        ctx.set_source_rgb(0.85, 0.75, 0.6)
        ctx.set_line_width(30)
        ctx.stroke()

    def draw(self, ctx, t):
        self._ring(ctx, True)
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        for k in range(5):
            ctx.rectangle(-200, -500 + k * 55 + 10 * math.sin(t + k), 400, 20)
        ctx.set_source_rgba(0.85, 0.6, 0.35, 0.6)
        ctx.fill()
        ctx.restore()
        self._ring(ctx, False)
        face(ctx, 0, -410, 1.0, t, 0.8)

    def inside(self, ctx, t):
        for r, c in ((160, (0.9, 0.7, 0.4)), (90, (0.6, 0.7, 0.9)), (40, (0.8, 0.6, 0.4))):
            ctx.arc(0, -380, r, 0, 2 * math.pi)
            ctx.set_source_rgb(*c)
            ctx.fill()


class BlackHole(Thing):
    float_ = True
    color = (0.05, 0.05, 0.08)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -380, 120, 0, 2 * math.pi)

    def draw(self, ctx, t):
        for k in range(40):  # disco de acreción girando
            a = t * (2 + k % 5 * 0.3) + k * 0.6
            r = 160 + (k * 13) % 150
            ctx.arc(math.cos(a) * r, -380 + math.sin(a) * r * 0.32, 8 + k % 4 * 3, 0, 2 * math.pi)
            ctx.set_source_rgba(1.0, 0.5 + (k % 5) * 0.1, 0.2, 0.8)
            ctx.fill()
        glow(ctx, 0, -380, 230, (1, 0.6, 0.3), 0.5)
        self.body(ctx, t)
        ctx.set_source_rgb(0, 0, 0)
        ctx.fill()
        ctx.arc(0, -380, 128, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.75, 0.4)
        ctx.set_line_width(8)
        ctx.stroke()

    def inside(self, ctx, t):
        for k in range(5):
            ph = (t * 0.6 + k / 5) % 1
            ctx.arc(0, -380, 110 * (1 - ph), 0, 2 * math.pi)
            ctx.set_source_rgba(0.6, 0.8, 1, ph)
            ctx.set_line_width(5)
            ctx.stroke()
        ctx.arc(0, -380, 8, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()


class Comet(Thing):
    float_ = True
    color = (0.7, 0.85, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(-150, -450, 80, 0, 2 * math.pi)

    def draw(self, ctx, t):
        for k in range(6):
            w = 1 + 0.1 * math.sin(t * 6 + k)
            poly(ctx, [(-160, -520 + k * 6), (300 + k * 40, -380 - 60 * w + k * 25), (300 + k * 30, -300 + k * 20), (-160, -380)])
            ctx.set_source_rgba(0.6, 0.85, 1.0, 0.18)
            ctx.fill()
        self.body(ctx, t)
        outline(ctx, (0.75, 0.75, 0.8))
        face(ctx, -150, -460, 0.8, t, 0.4)

    def inside(self, ctx, t):
        ctx.arc(-150, -450, 50, 0, 2 * math.pi)
        ctx.set_source_rgb(0.85, 0.95, 1)
        ctx.fill()
        bubbles_up(ctx, t, -150, -420, -500, 6, (0.8, 0.95, 1), 7)


class Satellite(Thing):
    float_ = True
    color = (0.85, 0.75, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -80, -500, 80, -340, 16)

    def draw(self, ctx, t):
        for sx in (-1, 1):
            ctx.rectangle(sx * 80 if sx > 0 else -280, -450, 200, 60)
            outline(ctx, (0.25, 0.35, 0.7))
            for k in range(4):
                ctx.move_to((sx * 80 if sx > 0 else -280) + k * 50, -450)
                ctx.rel_line_to(0, 60)
            ctx.set_source_rgba(1, 1, 1, 0.5)
            ctx.set_line_width(3)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.arc(0, -540, 50, math.pi * 0.1, math.pi * 0.9)
        outline(ctx, (0.9, 0.9, 0.92), 7)
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1
            ctx.arc(0, -560, 40 + ph * 150, -2.4, -0.7)
            ctx.set_source_rgba(0.4, 0.9, 1, 1 - ph)
            ctx.set_line_width(6)
            ctx.stroke()

    def inside(self, ctx, t):
        gear(ctx, -30, -440, 30, t * 2)
        rrect(ctx, 10, -480, 60, -380, 8)
        ctx.set_source_rgb(0.3, 1, 0.5)
        ctx.fill()


# ---------------------------------------------------------------- vehículos
class Car(Thing):
    color = (0.95, 0.3, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -290, -260, 290, -90, 40)
        ctx.new_sub_path()
        poly(ctx, [(-170, -260), (-100, -380), (120, -380), (200, -260)])

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for x0, x1 in ((-140, -10), (10, 150)):
            poly(ctx, [(x0, -270), (x0 + 30 if x0 < 0 else x0, -360), (x1 - 10 if x1 > 0 else x1, -360), (x1 + 30 if x1 > 0 else x1, -270)])
            outline(ctx, (0.7, 0.9, 1.0), 7)
        for x in (-170, 170):
            ctx.save()
            ctx.translate(x, -80)
            ctx.rotate(-t * 8)
            ctx.arc(0, 0, 70, 0, 2 * math.pi)
            outline(ctx, (0.2, 0.2, 0.22))
            ctx.arc(0, 0, 30, 0, 2 * math.pi)
            outline(ctx, (0.8, 0.8, 0.85), 6)
            ctx.move_to(-30, 0)
            ctx.line_to(30, 0)
            ctx.set_line_width(6)
            ctx.stroke()
            ctx.restore()
        ctx.arc(-280, -190, 22, 0, 2 * math.pi)
        outline(ctx, (1, 0.95, 0.6), 6)
        for k in range(3):
            ph = (t * 2 + k / 3) % 1
            ctx.arc(320 + ph * 120, -120 - ph * 30, 15 + ph * 25, 0, 2 * math.pi)
            ctx.set_source_rgba(0.7, 0.7, 0.75, 1 - ph)
            ctx.fill()

    def inside(self, ctx, t):
        for k in range(4):  # pistones
            y = -200 + 30 * math.sin(t * 12 + k * math.pi / 2)
            ctx.rectangle(-250 + k * 45, y - 30, 32, 60)
            ctx.set_source_rgb(0.8, 0.82, 0.88)
            ctx.fill()
        glow(ctx, -170, -200, 90, (1, 0.6, 0.2), 0.6)
        flow_line(ctx, [(-60, -180), (100, -180), (250, -150)], t, (1, 0.8, 0.3), 8)
        for x in (60, 170):
            ctx.arc(x, -300, 30, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.7)
            ctx.fill()


class Plane(Thing):
    float_ = True
    color = (0.95, 0.96, 0.98)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-330, -420)
        ctx.curve_to(-330, -480, -250, -490, -200, -490)
        ctx.line_to(260, -480)
        ctx.line_to(330, -560)
        ctx.line_to(350, -420)
        ctx.curve_to(100, -370, -250, -360, -330, -420)
        ctx.close_path()

    def draw(self, ctx, t):
        for k in range(3):
            ctx.move_to(360, -440 + k * 10)
            ctx.line_to(560, -440 + k * 10 + 5 * math.sin(t * 4 + k))
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.set_line_width(6)
            ctx.stroke()
        poly(ctx, [(-40, -440), (120, -440), (220, -260), (160, -260)])
        outline(ctx, (0.3, 0.5, 0.9))
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(7):
            ctx.arc(-200 + k * 60, -450, 14, 0, 2 * math.pi)
            outline(ctx, (0.6, 0.85, 1.0), 4)
        poly(ctx, [(-300, -460), (-250, -480), (-230, -450), (-290, -440)])
        outline(ctx, (0.3, 0.3, 0.4), 4)

    def inside(self, ctx, t):
        for k in range(8):
            ctx.arc(-200 + k * 55, -430, 16, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.7)
            ctx.fill()
        flow_line(ctx, [(300, -440), (-280, -430)], t, (1, 0.9, 0.4), 4)


class Ship(Thing):
    color = (0.85, 0.25, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-320, -260), (320, -260), (250, -80), (-260, -80)])

    def draw(self, ctx, t):
        ctx.save()
        ctx.translate(0, 8 * math.sin(t * 1.5))
        ctx.rotate(0.03 * math.sin(t * 1.5))
        rrect(ctx, -180, -400, 160, -260, 14)
        outline(ctx, (1, 1, 1))
        for k in range(5):
            ctx.arc(-130 + k * 60, -330, 14, 0, 2 * math.pi)
            outline(ctx, (0.6, 0.85, 1.0), 4)
        for x in (-80, 60):
            ctx.rectangle(x, -520, 60, 120)
            outline(ctx, (0.95, 0.75, 0.2))
            for k in range(3):
                ph = (t * 0.8 + k / 3) % 1
                ctx.arc(x + 30 + 30 * ph, -540 - ph * 150, 20 + 25 * ph, 0, 2 * math.pi)
                ctx.set_source_rgba(0.6, 0.6, 0.65, 1 - ph)
                ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(-300, -230, 600, 26)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.restore()
        ctx.move_to(-400, -90)
        for x in range(-400, 401, 25):
            ctx.line_to(x, -90 + 12 * math.sin(x / 40 + t * 3))
        ctx.line_to(400, 0)
        ctx.line_to(-400, 0)
        ctx.close_path()
        ctx.set_source_rgba(0.3, 0.6, 0.95, 0.85)
        ctx.fill()

    def inside(self, ctx, t):
        gear(ctx, -100, -170, 45, t * 3)
        gear(ctx, 0, -170, 35, -t * 4)
        glow(ctx, 130, -170, 80, (1, 0.6, 0.2), 0.7)
        flow_line(ctx, [(150, -170), (240, -120)], t, (0.6, 0.9, 1), 8)


class Submarine(Thing):
    float_ = True
    color = (1.0, 0.82, 0.2)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -380, 300, 120)

    def draw(self, ctx, t):
        rrect(ctx, -60, -560, 80, -480, 20)
        outline(ctx, self.color)
        ctx.move_to(30, -560)
        ctx.line_to(30, -650)
        ctx.line_to(-20, -650)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(16)
        ctx.stroke()
        ctx.save()
        ctx.translate(310, -380)
        ctx.rotate(t * 10)
        for k in range(3):
            ctx.rotate(2 * math.pi / 3)
            ellipse(ctx, 0, -40, 18, 40)
            ctx.set_source_rgb(0.5, 0.5, 0.55)
            ctx.fill()
        ctx.restore()
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(4):
            ctx.arc(-180 + k * 110, -390, 34, 0, 2 * math.pi)
            outline(ctx, (0.55, 0.85, 1.0), 7)
        bubbles_up(ctx, t, 330, -380, -700, 7, (0.8, 0.95, 1), 12)

    def inside(self, ctx, t):
        for k in range(4):
            ctx.arc(-180 + k * 110, -390, 18, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.7)
            ctx.fill()
        ellipse(ctx, 0, -330, 220, 30)
        ctx.set_source_rgba(0.4, 0.7, 1, 0.6)  # tanques de lastre
        ctx.fill()
        gear(ctx, 230, -380, 35, t * 5)


class Train(Thing):
    color = (0.25, 0.5, 0.35)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -300, -330, 120, -110, 20)
        ctx.new_sub_path()
        rrect(ctx, 60, -470, 300, -110, 20)

    def draw(self, ctx, t):
        ctx.rectangle(-250, -480, 70, 150)
        outline(ctx, (0.2, 0.2, 0.22))
        for k in range(5):
            ph = (t * 0.9 + k / 5) % 1
            ctx.arc(-215 + 60 * ph, -500 - ph * 250, 25 + 40 * ph, 0, 2 * math.pi)
            ctx.set_source_rgba(0.85, 0.85, 0.88, 1 - ph)
            ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(110, -430, 140, 110)
        outline(ctx, (0.7, 0.9, 1.0), 7)
        poly(ctx, [(-300, -150), (-380, -60), (-300, -60)])
        outline(ctx, (0.85, 0.25, 0.25))
        for x in (-220, -80, 60, 220):
            ctx.save()
            ctx.translate(x, -80)
            ctx.rotate(-t * 6)
            ctx.arc(0, 0, 55, 0, 2 * math.pi)
            outline(ctx, (0.85, 0.25, 0.25))
            ctx.move_to(-55, 0)
            ctx.line_to(55, 0)
            ctx.move_to(0, -55)
            ctx.line_to(0, 55)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
            ctx.restore()

    def inside(self, ctx, t):
        glow(ctx, 160, -200, 100, (1, 0.5, 0.15), 0.8)
        for k in range(6):
            ctx.arc(110 + (k % 3) * 40, -170 - (k // 3) * 30, 15, 0, 2 * math.pi)
            ctx.set_source_rgb(0.25, 0.25, 0.28)
            ctx.fill()
        rrect(ctx, -280, -300, 40, -170, 30)
        ctx.set_source_rgba(0.6, 0.85, 1, 0.5)  # caldera de vapor
        ctx.fill()
        bubbles_up(ctx, t, -120, -180, -300, 8, (1, 1, 1), 9, 100)


# ---------------------------------------------------------------- edificios y naturaleza
class House(Thing):
    color = (0.98, 0.85, 0.6)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-230, -380, 460, 380)
        ctx.new_sub_path()
        poly(ctx, [(-280, -370), (0, -620), (280, -370)])

    def draw(self, ctx, t):
        ctx.rectangle(120, -620, 70, 160)
        outline(ctx, (0.6, 0.35, 0.25))
        bubbles_up(ctx, t, 155, -630, -900, 6, (0.75, 0.75, 0.78), 30, 40)
        ctx.rectangle(-230, -380, 460, 380)
        outline(ctx, self.color)
        poly(ctx, [(-280, -370), (0, -620), (280, -370)])
        outline(ctx, (0.85, 0.3, 0.25))
        rrect(ctx, -50, -200, 50, 0, 10)
        outline(ctx, (0.6, 0.4, 0.25))
        for x in (-170, 90):
            ctx.rectangle(x, -310, 80, 80)
            on = math.sin(t * 2 + x) > 0
            outline(ctx, (1, 0.9, 0.5) if on else (0.7, 0.9, 1.0), 7)

    def inside(self, ctx, t):
        ctx.rectangle(-220, -200, 440, 8)
        ctx.set_source_rgb(0.9, 0.9, 0.95)
        ctx.fill()
        for (x, y) in ((-140, -260), (120, -100)):
            ctx.arc(x, y, 26, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.7)
            ctx.fill()
        flow_line(ctx, [(-200, -20), (-200, -350), (200, -350), (200, -20)], t, (0.4, 0.8, 1), 6)
        flow_line(ctx, [(0, -20), (0, -190)], t, (1, 0.85, 0.3), 6)


class Skyscraper(Thing):
    color = (0.7, 0.8, 0.92)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-130, -800, 260, 800)

    def draw(self, ctx, t):
        ctx.move_to(0, -800)
        ctx.line_to(0, -900)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(10)
        ctx.stroke()
        ctx.arc(0, -905, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.3 * (1 + math.sin(t * 5)), 0.3)
        ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        for y in range(-770, -40, 60):
            for x in (-100, -40, 20, 80):
                ctx.rectangle(x, y, 30, 36)
                on = (hash((x, y)) % 4 == 0) ^ (math.sin(t + x + y) > 0.9)
                ctx.set_source_rgb(*((1, 0.9, 0.5) if on else (0.45, 0.6, 0.8)))
                ctx.fill()

    def inside(self, ctx, t):
        for y in range(-760, 0, 60):
            ctx.rectangle(-120, y, 240, 4)
        ctx.set_source_rgba(0.9, 0.95, 1, 0.6)
        ctx.fill()
        y = -60 - 680 * (0.5 + 0.5 * math.sin(t * 0.8))
        ctx.rectangle(-25, y, 50, 55)
        ctx.set_source_rgb(1, 0.85, 0.3)
        ctx.fill()
        ctx.move_to(0, -800)
        ctx.line_to(0, y)
        ctx.set_source_rgb(0.8, 0.8, 0.85)
        ctx.set_line_width(3)
        ctx.stroke()


class Tree(Thing):
    color = (0.35, 0.75, 0.38)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-45, -330, 90, 330)
        for dx, dy, r in ((0, -560, 170), (-140, -450, 120), (140, -450, 120)):
            ctx.new_sub_path()
            ctx.arc(dx, dy, r, 0, 2 * math.pi)

    def draw(self, ctx, t):
        sw = 8 * math.sin(t * 1.5)
        ctx.rectangle(-45, -330, 90, 330)
        outline(ctx, (0.55, 0.36, 0.2))
        for dx, dy, r in ((0, -560, 170), (-140, -450, 120), (140, -450, 120)):
            ctx.new_sub_path()
            ctx.arc(dx + sw, dy, r, 0, 2 * math.pi)
        outline(ctx, self.color)
        for (x, y) in ((-80, -500), (60, -620), (120, -430), (-150, -400)):
            ctx.arc(x + sw, y, 22, 0, 2 * math.pi)
            outline(ctx, (0.95, 0.3, 0.3), 5)
        face(ctx, 0, -230, 0.8, t, 0.6)

    def inside(self, ctx, t):
        for k in range(5):
            flow_line(ctx, [(-100 + k * 50, 0), (-10 + k * 5, -200), (0, -330), (-120 + k * 60, -520)], t, (0.4, 0.75, 1), 6)
        for k in range(4):
            ph = (t * 0.5 + k / 4) % 1
            ctx.arc(-120 + k * 80, -650 - ph * 80, 10, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 1 - ph)  # oxígeno saliendo
            ctx.fill()


class Mushroom(Thing):
    color = (0.95, 0.3, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -380, 220, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.new_sub_path()
        rrect(ctx, -70, -390, 70, 0, 30)

    def draw(self, ctx, t):
        rrect(ctx, -70, -390, 70, 0, 30)
        outline(ctx, (0.98, 0.95, 0.88))
        ctx.arc(0, -380, 220, math.pi, 2 * math.pi)
        ctx.close_path()
        outline(ctx, self.color)
        for (x, y, r) in ((-110, -450, 30), (20, -540, 36), (120, -440, 26), (-30, -430, 20)):
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
        face(ctx, 0, -270, 0.8, t, 0.2)
        for k in range(6):
            ph = (t * 0.6 + k / 6) % 1
            ctx.arc(-150 + k * 60 + 30 * math.sin(t + k), -390 + ph * 300, 6, 0, 2 * math.pi)
            ctx.set_source_rgba(0.9, 0.8, 0.5, 1 - ph)
            ctx.fill()

    def inside(self, ctx, t):
        for k in range(9):  # micelio bajo tierra
            a = math.pi * (0.1 + 0.8 * k / 8)
            flow_line(ctx, [(0, -40), (math.cos(a) * 200, 30 + math.sin(a) * 40)], t, (1, 1, 0.8), 4)
        for k in range(8):
            ctx.move_to(-200 + k * 55, -385)
            ctx.line_to(-180 + k * 50, -410)
        ctx.set_source_rgb(1, 0.85, 0.85)
        ctx.set_line_width(4)
        ctx.stroke()


class Cactus(Thing):
    color = (0.35, 0.7, 0.4)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -70, -620, 70, 0, 70)
        rrect(ctx, -210, -450, -130, -230, 40)
        rrect(ctx, 130, -520, 210, -300, 40)

    def draw(self, ctx, t):
        poly(ctx, [(-150, -260), (-60, -300), (-60, -230)])
        ctx.rectangle(-170, -300, 110, 50)
        ctx.set_source_rgb(*self.color)
        ctx.fill()
        ctx.rectangle(60, -340, 110, 50)
        ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(10):
            y = -580 + k * 55
            for sx in (-1, 1):
                ctx.move_to(sx * 60, y)
                ctx.line_to(sx * 85, y - 10)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.arc(0, -640, 30 + 3 * math.sin(t * 3), 0, 2 * math.pi)
        outline(ctx, (1, 0.5, 0.7), 6)
        face(ctx, 0, -420, 0.7, t, 0.9)

    def inside(self, ctx, t):
        ctx.save()
        rrect(ctx, -60, -600, 60, -10, 60)
        ctx.clip()
        lvl = -450 + 30 * math.sin(t)
        ctx.rectangle(-70, lvl, 140, 600)
        ctx.set_source_rgba(0.35, 0.65, 1, 0.8)
        ctx.fill()
        ctx.restore()
        bubbles_up(ctx, t, 0, -20, -450, 6, (0.8, 0.95, 1), 8)


class Flower(Thing):
    color = (1.0, 0.5, 0.65)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -500, 150, 0, 2 * math.pi)

    def draw(self, ctx, t):
        sw = 10 * math.sin(t * 1.5)
        ctx.move_to(0, 0)
        ctx.curve_to(20, -150, -20, -300, sw, -480)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(30)
        ctx.stroke_preserve()
        ctx.set_source_rgb(0.3, 0.7, 0.35)
        ctx.set_line_width(18)
        ctx.stroke()
        for sx in (-1, 1):
            ctx.save()
            ctx.translate(0, -200)
            ctx.rotate(sx * (0.8 + 0.1 * math.sin(t * 2)))
            ellipse(ctx, 0, -60, 35, 70)
            ctx.restore()
            outline(ctx, (0.35, 0.75, 0.4), 7)
        ctx.save()
        ctx.translate(sw, -500)
        ctx.rotate(t * 0.3)
        for k in range(8):
            ctx.rotate(math.pi / 4)
            ellipse(ctx, 0, -100, 45, 70)
            outline(ctx, self.color, 7)
        ctx.restore()
        ctx.arc(sw, -500, 70, 0, 2 * math.pi)
        outline(ctx, (1, 0.85, 0.2))
        face(ctx, sw, -515, 0.6, t, 0.1)

    def inside(self, ctx, t):
        flow_line(ctx, [(0, 0), (0, -250), (0, -480)], t, (0.4, 0.75, 1), 8)
        for k in range(10):
            a = k * 0.63 + t
            ctx.arc(math.cos(a) * 45, -500 + math.sin(a) * 45, 8, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.9, 0.3)
            ctx.fill()


class Iceberg(Thing):
    float_ = True
    color = (0.88, 0.96, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-180, -380), (-80, -620), (40, -560), (150, -660), (220, -380), (300, -200), (200, 60),
                   (-160, 80), (-300, -150)])

    def draw(self, ctx, t):
        poly(ctx, [(-180, -380), (-80, -620), (40, -560), (150, -660), (220, -380)])
        outline(ctx, self.color)
        ctx.rectangle(-400, -380, 800, 480)
        ctx.set_source_rgba(0.25, 0.55, 0.9, 0.9)
        ctx.fill()
        ctx.move_to(-400, -380)
        for x in range(-400, 401, 25):
            ctx.line_to(x, -380 + 8 * math.sin(x / 30 + t * 3))
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(6)
        ctx.stroke()
        poly(ctx, [(-180, -370), (220, -370), (300, -200), (200, 60), (-160, 80), (-300, -150)])
        ctx.set_source_rgba(0.75, 0.9, 1.0, 0.35)  # la parte que no se ve (90 %)
        ctx.fill()
        face(ctx, 20, -480, 0.8, t, 0.6)

    def inside(self, ctx, t):
        poly(ctx, [(-180, -370), (220, -370), (300, -200), (200, 60), (-160, 80), (-300, -150)])
        ctx.set_source_rgba(0.6, 0.9, 1, 0.8)
        ctx.fill()
        for k in range(10):
            ctx.arc(-150 + (k * 71) % 380, -300 + (k * 53) % 320, 10, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.fill()


class Tornado(Thing):
    color = (0.7, 0.72, 0.78)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-260, -760), (260, -760), (40, 0), (-40, 0)])

    def draw(self, ctx, t):
        for k in range(12):
            y = -740 + k * 62
            w = 250 - k * 19
            off = 30 * math.sin(t * 3 + k * 0.5)
            ctx.save()
            ctx.translate(off, y)
            ctx.scale(1, 0.22)
            ctx.arc(0, 0, w, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(*shade(self.color, 1 - k * 0.02), 0.9)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(5)
            ctx.stroke()
        for k in range(5):  # escombros girando
            a = t * 4 + k * 1.3
            r = 180 - k * 25
            ctx.rectangle(math.cos(a) * r - 12, -600 + k * 110 + math.sin(a) * 20, 24, 24)
            ctx.set_source_rgb(0.55, 0.38, 0.22)
            ctx.fill()

    def inside(self, ctx, t):
        for k in range(8):
            a = t * 3 + k
            flow_line(ctx, [(math.cos(a) * 150, -100), (math.cos(a + 1) * 100, -400), (0, -700)], t * 2, (0.6, 0.9, 1), 5)


class StormCloud(Thing):
    float_ = True
    color = (0.5, 0.52, 0.6)

    def body(self, ctx, t):
        ctx.new_path()
        for dx, dy, r in ((-150, -500, 110), (-30, -580, 140), (120, -510, 120), (20, -460, 130)):
            ctx.new_sub_path()
            ctx.arc(dx, dy, r, 0, 2 * math.pi)

    def draw(self, ctx, t):
        for k in range(14):
            ph = (t * 1.5 + k / 14) % 1
            x = -200 + (k * 31) % 400
            ctx.move_to(x, -420 + ph * 420)
            ctx.line_to(x - 8, -390 + ph * 420)
            ctx.set_source_rgba(0.5, 0.7, 1, 0.9)
            ctx.set_line_width(6)
            ctx.stroke()
        if (t % 1.7) < 0.15:
            poly(ctx, [(0, -420), (60, -420), (10, -260), (70, -260), (-60, 0), (-10, -200), (-60, -200)])
            outline(ctx, (1, 0.95, 0.3), 6)
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, -10, -530, 0.9, t, 0.7)

    def inside(self, ctx, t):
        for k in range(10):
            a = t * 1.5 + k
            x, y = math.cos(a) * 160, -520 + math.sin(a * 1.3) * 80
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(50)
            ctx.move_to(x - 15, y + 15)
            ctx.set_source_rgb(*((1, 0.4, 0.4) if k % 2 else (0.4, 0.8, 1)))
            ctx.show_text("+" if k % 2 else "−")


# ---------------------------------------------------------------- tecnología y objetos
class LightBulb(Thing):
    color = (1.0, 0.92, 0.45)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -470, 180, math.pi * 0.78, math.pi * 2.22)
        ctx.line_to(70, -200)
        ctx.line_to(-70, -200)
        ctx.close_path()

    def draw(self, ctx, t):
        g = 0.7 + 0.3 * math.sin(t * 3)
        glow(ctx, 0, -470, 380, (1, 0.95, 0.5), 0.5 * g)
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(3):
            rrect(ctx, -75, -200 + k * 45, 75, -160 + k * 45, 14)
            outline(ctx, (0.7, 0.72, 0.78), 7)
        face(ctx, 0, -490, 1.0, t, 0.3)

    def inside(self, ctx, t):
        ctx.move_to(-30, -200)
        ctx.line_to(-30, -400)
        for k in range(6):
            ctx.line_to(-30 + k * 12, -420 - (k % 2) * 30)
        ctx.line_to(30, -400)
        ctx.line_to(30, -200)
        ctx.set_source_rgb(1, 0.8 + 0.2 * math.sin(t * 10), 0.3)
        ctx.set_line_width(8)
        ctx.stroke()
        flow_line(ctx, [(-30, -150), (-30, -400)], t * 2, (0.5, 0.9, 1), 4)


class Phone(Thing):
    color = (0.2, 0.22, 0.28)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -150, -700, 150, -80, 40)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        rrect(ctx, -125, -665, 125, -115, 22)
        ctx.set_source_rgb(0.4, 0.7, 1.0)
        ctx.fill()
        for k in range(3):  # notificaciones que entran
            ph = ((t * 0.8) - k * 0.3) % 2
            y = -620 + k * 110
            x = -110 + max(0, 1 - ph * 3) * 300
            rrect(ctx, x, y, x + 220, y + 85, 16)
            outline(ctx, (1, 1, 1), 5)
            ctx.arc(x + 40, y + 42, 22, 0, 2 * math.pi)
            ctx.set_source_rgb(*((1, 0.35, 0.35), (0.35, 0.85, 0.45), (1, 0.8, 0.2))[k])
            ctx.fill()

    def inside(self, ctx, t):
        rrect(ctx, -110, -380, 110, -130, 20)
        ctx.set_source_rgb(0.3, 0.85, 0.45)  # batería
        ctx.fill()
        ctx.rectangle(-60, -600, 120, 120)
        ctx.set_source_rgb(0.25, 0.25, 0.3)
        ctx.fill()
        for k in range(6):
            flow_line(ctx, [(-60, -590 + k * 20), (-110, -590 + k * 20)], t, (1, 0.85, 0.3), 3)
            flow_line(ctx, [(60, -590 + k * 20), (110, -590 + k * 20)], t, (1, 0.85, 0.3), 3)


class Computer(Thing):
    color = (0.8, 0.82, 0.88)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -280, -650, 280, -270, 24)

    def draw(self, ctx, t):
        poly(ctx, [(-50, -270), (50, -270), (90, -130), (-90, -130)])
        outline(ctx, self.color)
        rrect(ctx, -300, -140, 300, -90, 14)
        outline(ctx, self.color)
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(-250, -620, 500, 320)
        ctx.set_source_rgb(0.1, 0.12, 0.2)
        ctx.fill()
        rnd = random.Random(int(t * 4))
        for k in range(8):
            y = -590 + k * 38
            ctx.rectangle(-220 + (k % 3) * 30, y, rnd.uniform(80, 360), 16)
            ctx.set_source_rgb(*((0.4, 1, 0.5), (0.5, 0.8, 1), (1, 0.8, 0.3))[k % 3])
            ctx.fill()

    def inside(self, ctx, t):
        ctx.rectangle(-70, -530, 140, 140)
        ctx.set_source_rgb(0.25, 0.25, 0.3)
        ctx.fill()
        for k in range(7):
            flow_line(ctx, [(-70, -520 + k * 20), (-240, -520 + k * 20)], t, (0.4, 1, 0.6), 3)
            flow_line(ctx, [(70, -520 + k * 20), (240, -520 + k * 20)], t, (0.4, 1, 0.6), 3)
        glow(ctx, 0, -460, 80, (0.5, 0.9, 1), 0.6)


class Battery(Thing):
    color = (0.25, 0.25, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -130, -650, 130, -60, 30)

    def draw(self, ctx, t):
        rrect(ctx, -50, -700, 50, -640, 12)
        outline(ctx, (0.75, 0.75, 0.8))
        self.body(ctx, t)
        outline(ctx, self.color)
        lvl = 0.5 + 0.5 * math.sin(t * 0.9)
        for k in range(5):
            if k / 5 < lvl:
                ctx.rectangle(-100, -150 - k * 100, 200, 80)
                ctx.set_source_rgb(*((0.95, 0.3, 0.3) if lvl < 0.3 else (0.35, 0.9, 0.45)))
                ctx.fill()
        poly(ctx, [(10, -500), (-40, -360), (0, -360), (-20, -240), (40, -400), (0, -400)])
        outline(ctx, (1, 0.9, 0.2), 6)

    def inside(self, ctx, t):
        for k in range(14):
            ph = (t * 0.7 + k / 14) % 1
            ctx.arc(-80 + (k * 37) % 160, -100 - ph * 520, 10, 0, 2 * math.pi)
            ctx.set_source_rgb(*((1, 0.85, 0.3) if k % 2 else (0.5, 0.85, 1)))
            ctx.fill()


class Magnet(Thing):
    color = (0.92, 0.25, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -400, 210, math.pi, 2 * math.pi)
        ctx.line_to(210, -150)
        ctx.line_to(90, -150)
        ctx.line_to(90, -400)
        ctx.arc_negative(0, -400, 90, 0, math.pi)
        ctx.line_to(-90, -150)
        ctx.line_to(-210, -150)
        ctx.close_path()

    def draw(self, ctx, t):
        for k in range(4):
            ph = (t * 0.6 + k / 4) % 1
            ctx.arc(0, -150, 160 + ph * 200, 0.1, math.pi - 0.1)
            ctx.set_source_rgba(0.4, 0.7, 1, 1 - ph)
            ctx.set_line_width(6)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        for x in (-150, 150):
            ctx.rectangle(x - 60, -230, 120, 80)
            outline(ctx, (0.85, 0.85, 0.9), 8)

    def inside(self, ctx, t):
        for k in range(10):
            a = math.pi + k * math.pi / 9
            x, y = math.cos(a) * 150, -400 + math.sin(a) * 150
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(a + math.pi / 2 + 0.2 * math.sin(t * 3 + k) * 0)
            poly(ctx, [(-8, -25), (8, -25), (0, 25)])
            ctx.restore()
            ctx.set_source_rgb(1, 0.85, 0.3)
            ctx.fill()


class MoneyBag(Thing):
    color = (0.85, 0.7, 0.45)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-60, -470)
        ctx.curve_to(-280, -380, -260, 0, 0, 0)
        ctx.curve_to(260, 0, 280, -380, 60, -470)
        ctx.close_path()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        poly(ctx, [(-60, -470), (-110, -580), (0, -540), (110, -580), (60, -470)])
        outline(ctx, self.color)
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(200)
        ctx.move_to(-60, -150)
        ctx.text_path("$")
        outline(ctx, (0.3, 0.6, 0.3), 8)
        for k in range(3):
            ph = (t * 0.8 + k / 3) % 1
            y = -300 - ph * 300
            ctx.arc(-200 + k * 200, y, 30, 0, 2 * math.pi)
            outline(ctx, (1, 0.8, 0.2), 5)

    def inside(self, ctx, t):
        for k in range(16):
            ctx.arc(-140 + (k % 5) * 70, -60 - (k // 5) * 60 - 5 * math.sin(t * 3 + k), 32, 0, 2 * math.pi)
            outline(ctx, (1, 0.82, 0.2), 4)


class Diamond(Thing):
    color = (0.6, 0.9, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-220, -480), (-120, -600), (120, -600), (220, -480), (0, -140)])

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for a, b in (((-220, -480), (220, -480)), ((-120, -600), (-60, -480)), ((120, -600), (60, -480)),
                     ((-60, -480), (0, -140)), ((60, -480), (0, -140)), ((0, -600), (-60, -480)), ((0, -600), (60, -480))):
            ctx.move_to(*a)
            ctx.line_to(*b)
        ctx.set_source_rgba(*INK, 0.5)
        ctx.set_line_width(5)
        ctx.stroke()
        for k in range(4):
            s = abs(math.sin(t * 2 + k * 1.5))
            cx, cy = [(-150, -560), (180, -520), (40, -380), (-90, -640)][k]
            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale(s, s)
            poly(ctx, [(0, -40), (10, -10), (40, 0), (10, 10), (0, 40), (-10, 10), (-40, 0), (-10, -10)])
            ctx.restore()
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()

    def inside(self, ctx, t):
        pts = [(-120 + (k % 4) * 80, -540 + (k // 4) * 90) for k in range(12)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:]:
                if math.hypot(a[0] - b[0], a[1] - b[1]) < 125:
                    ctx.move_to(*a)
                    ctx.line_to(*b)
        ctx.set_source_rgba(0.8, 0.95, 1, 0.8)
        ctx.set_line_width(4)
        ctx.stroke()
        for (x, y) in pts:
            ctx.arc(x, y + 4 * math.sin(t * 4 + x), 14, 0, 2 * math.pi)
            ctx.set_source_rgb(0.3, 0.3, 0.35)
            ctx.fill()


class Treasure(Thing):
    color = (0.6, 0.4, 0.22)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-260, -330, 520, 330)

    def draw(self, ctx, t):
        op = 0.5 + 0.5 * math.sin(t * 1.2)
        glow(ctx, 0, -340, 300 * op, (1, 0.85, 0.3), 0.6)
        for k in range(8):
            ctx.arc(-180 + k * 50, -330 - 20 * math.sin(k), 30, 0, 2 * math.pi)
            outline(ctx, (1, 0.82, 0.2), 4)
        ctx.save()
        ctx.translate(0, -330)
        ctx.scale(1, 1 - op * 1.7)
        ctx.arc(0, 0, 260, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.restore()
        outline(ctx, shade(self.color, 1.1))
        self.body(ctx, t)
        outline(ctx, self.color)
        for x in (-200, 200):
            ctx.rectangle(x - 20, -330, 40, 330)
            outline(ctx, (1, 0.82, 0.2), 6)
        rrect(ctx, -40, -260, 40, -170, 12)
        outline(ctx, (1, 0.82, 0.2), 6)

    def inside(self, ctx, t):
        for k in range(20):
            ctx.arc(-220 + (k % 7) * 70, -40 - (k // 7) * 70, 30, 0, 2 * math.pi)
            outline(ctx, (1, 0.82, 0.2), 4)
        poly(ctx, [(0, -300), (40, -250), (0, -200), (-40, -250)])
        ctx.set_source_rgb(0.4, 0.9, 1)
        ctx.fill()


class Clock(Thing):
    color = (0.98, 0.98, 0.98)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -400, 230, 0, 2 * math.pi)

    def draw(self, ctx, t):
        for sx in (-1, 1):
            ctx.arc(sx * 160, -600, 60, 0, 2 * math.pi)
            outline(ctx, (0.95, 0.3, 0.3))
        self.body(ctx, t)
        outline(ctx, self.color, 14)
        for k in range(12):
            a = k * math.pi / 6
            ctx.move_to(math.cos(a) * 190, -400 + math.sin(a) * 190)
            ctx.line_to(math.cos(a) * 215, -400 + math.sin(a) * 215)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(8)
        ctx.stroke()
        for (L, w, sp) in ((120, 14, 0.5), (170, 9, 4)):
            a = t * sp - math.pi / 2
            ctx.move_to(0, -400)
            ctx.line_to(math.cos(a) * L, -400 + math.sin(a) * L)
            ctx.set_line_width(w)
            ctx.stroke()
        for sx in (-1, 1):
            ctx.move_to(sx * 140, -200)
            ctx.line_to(sx * 180, -10)
        ctx.set_line_width(14)
        ctx.stroke()

    def inside(self, ctx, t):
        gear(ctx, -60, -440, 70, t * 2, (1, 0.82, 0.3))
        gear(ctx, 70, -380, 50, -t * 2.8, (0.8, 0.85, 0.9))
        gear(ctx, -20, -310, 35, t * 4, (1, 0.7, 0.3))
        ctx.save()
        ctx.translate(0, -400)
        ctx.rotate(0.6 * math.sin(t * 6))
        ctx.move_to(0, 0)
        ctx.line_to(0, 160)
        ctx.set_source_rgb(0.8, 0.8, 0.85)
        ctx.set_line_width(6)
        ctx.stroke()
        ctx.restore()


class Hourglass(Thing):
    color = (0.85, 0.95, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-170, -680), (170, -680), (25, -380), (170, -80), (-170, -80), (-25, -380)])

    def draw(self, ctx, t):
        k = (t * 0.25) % 1
        self.body(ctx, t)
        ctx.set_source_rgba(*self.color, 0.6)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(10)
        ctx.stroke()
        top = -400 - 220 * (1 - k)
        poly(ctx, [(-150 * (1 - k) - 25 * k, top), (150 * (1 - k) + 25 * k, top), (25, -390), (-25, -390)])
        ctx.set_source_rgb(1, 0.82, 0.45)
        ctx.fill()
        ctx.rectangle(-4, -390, 8, 300)
        ctx.fill()
        h = 220 * k
        poly(ctx, [(-150, -90), (150, -90), (60, -90 - h), (-60, -90 - h)])
        ctx.fill()
        for y in (-700, -60):
            rrect(ctx, -210, y - 20, 210, y + 20, 14)
            outline(ctx, (0.6, 0.4, 0.22))

    def inside(self, ctx, t):
        for j in range(12):
            ph = (t * 1.5 + j / 12) % 1
            ctx.arc(4 * math.sin(j), -390 + ph * 290, 6, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.9, 0.5)
            ctx.fill()


class Book(Thing):
    color = (0.35, 0.5, 0.95)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-300, -560, 600, 400)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for sx in (-1, 1):
            ctx.rectangle(0 if sx > 0 else -280, -540, 280, 360)
            outline(ctx, (1, 0.98, 0.92), 6)
            for k in range(7):
                ctx.rectangle(30 if sx > 0 else -250, -500 + k * 45, 200, 10)
                ctx.set_source_rgba(*INK, 0.35)
                ctx.fill()
        ph = (t * 0.8) % 1
        ctx.save()
        ctx.scale(math.cos(ph * math.pi), 1)
        ctx.rectangle(0, -540, 280, 360)
        ctx.restore()
        outline(ctx, (1, 0.96, 0.88), 5)

    def inside(self, ctx, t):
        for k in range(8):
            ph = (t * 0.7 + k / 8) % 1
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(50)
            ctx.move_to(-200 + k * 55, -300 - ph * 250)
            ctx.set_source_rgba(1, 0.9, 0.4, 1 - ph)
            ctx.show_text("ABCDEFGH"[k])


class Telescope(Thing):
    color = (0.35, 0.4, 0.75)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -420)
        ctx.rotate(-0.5)
        rrect(ctx, -260, -60, 260, 60, 30)
        ctx.restore()

    def draw(self, ctx, t):
        for sx in (-1, 0, 1):
            ctx.move_to(0, -380)
            ctx.line_to(sx * 180, 0)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(16)
        ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.save()
        ctx.translate(0, -420)
        ctx.rotate(-0.5)
        ellipse(ctx, 260, 0, 24, 70)
        outline(ctx, (0.7, 0.9, 1.0), 7)
        ctx.restore()

    def inside(self, ctx, t):
        ctx.save()
        ctx.translate(0, -420)
        ctx.rotate(-0.5)
        for x in (150, -150):
            ellipse(ctx, x, 0, 15, 50)
            ctx.set_source_rgba(0.6, 0.9, 1, 0.9)
            ctx.fill()
        for dy in (-40, 40):
            flow_line(ctx, [(260, dy), (150, dy * 0.8), (-150, -dy * 0.3), (-260, 0)], -t, (1, 1, 0.6), 4)
        ctx.restore()


class Bomb(Thing):
    color = (0.25, 0.25, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -280, 230, 0, 2 * math.pi)

    def draw(self, ctx, t):
        ctx.move_to(120, -470)
        ctx.curve_to(180, -580, 260, -560, 260, -640)
        ctx.set_source_rgb(0.6, 0.5, 0.35)
        ctx.set_line_width(14)
        ctx.stroke()
        for k in range(6):
            a = t * 9 + k
            ctx.move_to(260, -640)
            ctx.line_to(260 + math.cos(a) * 50, -640 + math.sin(a) * 50)
        ctx.set_source_rgb(1, 0.75, 0.2)
        ctx.set_line_width(6)
        ctx.stroke()
        rrect(ctx, 60, -520, 180, -440, 14)
        outline(ctx, (0.4, 0.4, 0.45))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.arc(-80, -380, 50, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.fill()
        face(ctx, 0, -300, 1.1, t, 0.9)

    def inside(self, ctx, t):
        rrect(ctx, -110, -340, 110, -220, 16)
        ctx.set_source_rgb(0.1, 0.1, 0.12)
        ctx.fill()
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(70)
        ctx.move_to(-90, -255)
        ctx.set_source_rgb(1, 0.3, 0.3)
        ctx.show_text(f"0:{max(0, 9 - int(t * 2) % 10):02d}")
        for k, c in enumerate(((1, 0.3, 0.3), (0.3, 0.6, 1), (1, 0.9, 0.3))):
            ctx.move_to(-110, -300 + k * 30)
            ctx.curve_to(-180, -200, -100, -120, 0, -100 - k * 20)
            ctx.set_source_rgb(*c)
            ctx.set_line_width(8)
            ctx.stroke()


# ---------------------------------------------------------------- cuerpo humano (órganos grandes) y micro
class HeartOrgan(Thing):
    color = (0.9, 0.25, 0.3)

    def body(self, ctx, t):
        s = 1 + 0.08 * beat(t)
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -380)
        ctx.scale(s, s)
        ctx.move_to(0, 250)
        ctx.curve_to(-330, 40, -230, -300, 0, -150)
        ctx.curve_to(230, -300, 330, 40, 0, 250)
        ctx.close_path()
        ctx.restore()

    def draw(self, ctx, t):
        for x, c in ((-70, (0.3, 0.45, 0.9)), (60, (0.9, 0.3, 0.3))):
            ctx.move_to(x, -500)
            ctx.curve_to(x, -620, x + 80, -650, x + 120, -640)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(64)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(48)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -400, 1.0, t, 0.5)

    def inside(self, ctx, t):
        for (x, y, c) in ((-80, -450, (0.4, 0.55, 1)), (80, -450, (1, 0.45, 0.45)), (-60, -300, (0.4, 0.55, 1)),
                          (60, -300, (1, 0.45, 0.45))):
            ellipse(ctx, x, y, 60, 70 * (1 + 0.15 * beat(t + (0.1 if y < -350 else 0))))
            ctx.set_source_rgba(*c, 0.9)
            ctx.fill()
        flow_line(ctx, [(-60, -600), (-80, -450), (-60, -300)], t, (0.5, 0.7, 1), 8)
        flow_line(ctx, [(60, -300), (80, -450), (100, -620)], t, (1, 0.5, 0.5), 8)


class BrainOrgan(Thing):
    color = (1.0, 0.68, 0.8)

    def body(self, ctx, t):
        ctx.new_path()
        for (a, b, c) in ((-110, -480, 150), (100, -490, 150), (-130, -370, 130), (120, -370, 135), (0, -440, 150)):
            ctx.new_sub_path()
            ctx.arc(a, b, c, 0, 2 * math.pi)

    def draw(self, ctx, t):
        ctx.move_to(40, -260)
        ctx.line_to(60, -120)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(70)
        ctx.stroke_preserve()
        ctx.set_source_rgb(1, 0.6, 0.72)
        ctx.set_line_width(54)
        ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(7):
            x = -200 + k * 65
            ctx.move_to(x, -560 + (k % 2) * 40)
            ctx.curve_to(x + 40, -500, x - 20, -440, x + 30, -380)
        ctx.set_source_rgba(*INK, 0.4)
        ctx.set_line_width(6)
        ctx.stroke()
        face(ctx, 0, -430, 1.0, t, 0.2)

    def inside(self, ctx, t):
        pts = [(-180, -500), (-60, -560), (80, -520), (190, -440), (-150, -360), (0, -400), (130, -340), (-40, -300)]
        for i, a in enumerate(pts):
            for b in pts[i + 1:i + 3]:
                flow_line(ctx, [a, b], t * 1.5, (1, 1, 0.5), 3)
        for k, (x, y) in enumerate(pts):
            on = abs(math.sin(t * 3 + k * 1.3))
            ctx.arc(x, y, 14 + 8 * on, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.6, 0.4 + 0.6 * on)
            ctx.fill()


class LungsOrgan(Thing):
    color = (1.0, 0.6, 0.68)

    def body(self, ctx, t):
        b = 1 + 0.1 * math.sin(t * 1.8)
        ctx.new_path()
        for sx in (-1, 1):
            ctx.new_sub_path()
            ellipse(ctx, sx * 140, -330, 120 * b, 230 * b)

    def draw(self, ctx, t):
        ctx.move_to(0, -680)
        ctx.line_to(0, -480)
        ctx.line_to(-100, -400)
        ctx.move_to(0, -480)
        ctx.line_to(100, -400)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(50)
        ctx.stroke_preserve()
        ctx.set_source_rgb(0.9, 0.85, 0.9)
        ctx.set_line_width(34)
        ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -250, 0.8, t, 0.4)

    def inside(self, ctx, t):
        b = 1 + 0.1 * math.sin(t * 1.8)
        for sx in (-1, 1):
            for k in range(14):
                ang = k * 0.45
                x = sx * 140 + math.cos(ang) * 70 * b * (0.4 + k / 20)
                y = -330 + math.sin(ang * 1.7) * 160 * b * (k / 14)
                ctx.arc(x, y, 18 * b, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 0.75, 0.8, 0.9)
                ctx.fill()
                ctx.arc(x, y, 6, 0, 2 * math.pi)
                ctx.set_source_rgb(0.5, 0.75, 1)
                ctx.fill()


class StomachOrgan(Thing):
    color = (1.0, 0.7, 0.55)

    def body(self, ctx, t):
        w = 1 + 0.05 * math.sin(t * 2)
        ctx.new_path()
        ctx.move_to(-60, -620)
        ctx.curve_to(-40, -500, -260 * w, -520, -240 * w, -330)
        ctx.curve_to(-220, -120, 200 * w, -120, 230 * w, -330)
        ctx.curve_to(250, -460, 40, -470, 40, -620)
        ctx.close_path()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -330, 0.9, t, 0.6)

    def inside(self, ctx, t):
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        ctx.rectangle(-300, -330 + 15 * math.sin(t * 2), 600, 300)
        ctx.set_source_rgba(0.75, 1, 0.4, 0.7)  # jugos gástricos
        ctx.fill()
        ctx.restore()
        bubbles_up(ctx, t, 0, -170, -330, 10, (0.9, 1, 0.6), 12, 150)
        for k in range(5):
            a = t * 1.5 + k
            ctx.arc(math.cos(a) * 110, -260 + math.sin(a) * 40, 22, 0, 2 * math.pi)
            ctx.set_source_rgb(0.75, 0.5, 0.3)
            ctx.fill()


class Tooth(Thing):
    color = (0.98, 0.98, 0.95)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-180, -560)
        ctx.curve_to(-180, -700, -40, -680, 0, -620)
        ctx.curve_to(40, -680, 180, -700, 180, -560)
        ctx.curve_to(180, -420, 140, -300, 110, -100)
        ctx.curve_to(90, 0, 40, 0, 20, -180)
        ctx.line_to(-20, -180)
        ctx.curve_to(-40, 0, -90, 0, -110, -100)
        ctx.curve_to(-140, -300, -180, -420, -180, -560)
        ctx.close_path()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -500, 1.0, t, 0.2)

    def inside(self, ctx, t):
        ctx.move_to(-100, -560)
        ctx.curve_to(-100, -440, -70, -300, -60, -120)
        ctx.line_to(60, -120)
        ctx.curve_to(70, -300, 100, -440, 100, -560)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.5, 0.6, 0.85)
        ctx.fill()
        flow_line(ctx, [(-60, -30), (-50, -300), (0, -500)], t, (1, 0.3, 0.35), 6)
        flow_line(ctx, [(60, -30), (50, -300), (0, -500)], t, (1, 1, 0.5), 4)


class EyeOrgan(Thing):
    float_ = True
    color = (1, 1, 1)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -400, 220, 0, 2 * math.pi)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(5):
            ctx.move_to(200 * math.cos(k), -400 + 200 * math.sin(k))
            ctx.line_to(140 * math.cos(k + 0.2), -400 + 140 * math.sin(k + 0.2))
        ctx.set_source_rgb(0.95, 0.4, 0.4)
        ctx.set_line_width(4)
        ctx.stroke()
        lx = 40 * math.sin(t * 1.2)
        ctx.arc(-60 + lx, -400, 110, 0, 2 * math.pi)
        outline(ctx, (0.3, 0.6, 0.85))
        pupil = 45 + 20 * math.sin(t * 2)
        ctx.arc(-60 + lx, -400, pupil, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        ctx.arc(-90 + lx, -430, 18, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()

    def inside(self, ctx, t):
        ellipse(ctx, -150, -400, 30, 80)
        ctx.set_source_rgba(0.7, 0.9, 1, 0.9)  # cristalino
        ctx.fill()
        ctx.arc(0, -400, 200, -0.9, 0.9)
        ctx.set_source_rgb(1, 0.5, 0.4)  # retina
        ctx.set_line_width(14)
        ctx.stroke()
        for dy in (-60, 60):
            flow_line(ctx, [(-260, -400 + dy), (-150, -400 + dy * 0.6), (180, -400 - dy * 0.5)], t, (1, 1, 0.6), 4)
        flow_line(ctx, [(200, -400), (300, -380)], t, (1, 0.9, 0.4), 10)


class Bacteria(Thing):
    float_ = True
    color = (0.5, 0.85, 0.45)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -230, -470, 230, -290, 90)

    def draw(self, ctx, t):
        for k in range(5):
            ctx.move_to(230, -380 + (k - 2) * 25)
            for j in range(1, 11):
                ctx.line_to(230 + j * 25, -380 + (k - 2) * 30 + 20 * math.sin(t * 8 + j * 0.8 + k))
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(5)
            ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(10):
            ctx.new_sub_path()
            ctx.arc(-200 + k * 45, -470, 6, 0, 2 * math.pi)
            ctx.new_sub_path()
            ctx.arc(-200 + k * 45, -290, 6, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        face(ctx, -100, -400, 0.8, t, 0.8)

    def inside(self, ctx, t):
        ctx.save()
        ctx.translate(40, -380)
        ctx.rotate(t * 0.5)
        ctx.arc(0, 0, 70, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.9, 0.5, 1)
        ctx.set_line_width(8)
        ctx.stroke()
        for k in range(8):
            ctx.arc(-160 + k * 45, -340 + 30 * math.sin(k + t), 9, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.9, 0.4)
            ctx.fill()


class VirusBig(Thing):
    float_ = True
    color = (0.55, 0.85, 0.4)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -400, 170, 0, 2 * math.pi)

    def draw(self, ctx, t):
        ctx.save()
        ctx.translate(0, -400)
        ctx.rotate(t * 0.4)
        for k in range(14):
            ctx.rotate(2 * math.pi / 14)
            ctx.move_to(165, 0)
            ctx.line_to(240, 0)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(14)
            ctx.stroke()
            ctx.arc(255, 0, 24, 0, 2 * math.pi)
            outline(ctx, (0.95, 0.4, 0.45), 6)
        ctx.restore()
        self.body(ctx, t)
        outline(ctx, self.color)
        face(ctx, 0, -420, 1.0, t, 0.2)

    def inside(self, ctx, t):
        ctx.move_to(-120, -400)
        for j in range(25):
            a = j * 0.5 + t
            ctx.line_to(-120 + j * 10, -400 + 60 * math.sin(a))
        ctx.set_source_rgb(1, 0.85, 0.3)
        ctx.set_line_width(8)
        ctx.stroke()


class Cell(Thing):
    float_ = True
    color = (0.75, 0.9, 1.0)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -400)
        ctx.scale(1 + 0.04 * math.sin(t * 2), 1 - 0.04 * math.sin(t * 2))
        ctx.arc(0, 0, 250, 0, 2 * math.pi)
        ctx.restore()

    def draw(self, ctx, t):
        self.body(ctx, t)
        ctx.set_source_rgba(*self.color, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(11)
        ctx.stroke()
        ctx.arc(20, -400, 85, 0, 2 * math.pi)
        outline(ctx, (0.65, 0.45, 0.9))
        for k in range(4):
            a = t * 0.6 + k * 1.6
            ellipse(ctx, math.cos(a) * 160, -400 + math.sin(a) * 150, 40, 20)
            outline(ctx, (1, 0.6, 0.4), 5)

    def inside(self, ctx, t):
        self.draw(ctx, t)
        ctx.move_to(-20, -420)
        for j in range(10):
            ctx.line_to(-20 + j * 8, -420 + 25 * math.sin(j + t * 3))
        ctx.set_source_rgb(1, 1, 0.5)
        ctx.set_line_width(5)
        ctx.stroke()
        for k in range(10):
            a = k * 0.63 + t * 0.4
            ctx.arc(math.cos(a) * 200, -400 + math.sin(a) * 190, 8, 0, 2 * math.pi)
            ctx.set_source_rgb(0.4, 1, 0.6)
            ctx.fill()


class DNABig(Thing):
    float_ = True
    color = (0.65, 0.45, 0.95)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-150, -760, 300, 700)

    def draw(self, ctx, t):
        for k in range(24):
            y = -740 + k * 29
            ph = y / 60 + t * 2.5
            x1, x2 = math.sin(ph) * 130, -math.sin(ph) * 130
            ctx.move_to(x1, y)
            ctx.line_to(x2, y)
            ctx.set_source_rgb(*((1, 0.8, 0.3) if k % 2 else (0.4, 0.85, 1)))
            ctx.set_line_width(12)
            ctx.stroke()
            for x, z in ((x1, math.cos(ph)), (x2, -math.cos(ph))):
                ctx.arc(x, y, 16 + 5 * z, 0, 2 * math.pi)
                outline(ctx, self.color, 5)

    def body_clip(self):
        pass

    def inside(self, ctx, t):
        self.draw(ctx, t)


class AtomBig(Thing):
    float_ = True
    color = (1.0, 0.85, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -400, 90, 0, 2 * math.pi)

    def draw(self, ctx, t):
        for k in range(3):
            ctx.save()
            ctx.translate(0, -400)
            ctx.rotate(k * math.pi / 3)
            ctx.scale(1, 0.35)
            ctx.arc(0, 0, 280, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
            a = t * (2 + k)
            ex, ey = math.cos(a) * 280, math.sin(a) * 280 * 0.35
            ca, sa = math.cos(k * math.pi / 3), math.sin(k * math.pi / 3)
            ctx.arc(ex * ca - ey * sa, -400 + ex * sa + ey * ca, 26, 0, 2 * math.pi)
            outline(ctx, (0.4, 0.75, 1), 6)
        for j in range(9):
            a = j * 0.7
            ctx.arc(math.cos(a) * 40, -400 + math.sin(a) * 40, 32, 0, 2 * math.pi)
            outline(ctx, (0.95, 0.35, 0.3) if j % 2 else (0.6, 0.65, 0.9), 5)

    def inside(self, ctx, t):
        for j in range(9):
            a = j * 0.7 + t
            ctx.arc(math.cos(a) * 45, -400 + math.sin(a) * 45, 20, 0, 2 * math.pi)
            ctx.set_source_rgb(*((1, 0.5, 0.4) if j % 2 else (0.7, 0.75, 1)))
            ctx.fill()
        glow(ctx, 0, -400, 90, (1, 1, 0.6), 0.6)


# ---------------------------------------------------------------- comida, deporte y otros
class Egg(Thing):
    color = (1.0, 0.97, 0.9)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -300)
        ctx.rotate(0.08 * math.sin(t * 6) * (math.sin(t) > 0.3))
        ellipse(ctx, 0, 0, 180, 240)
        ctx.restore()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        poly(ctx, [(-80, -380), (-40, -340), (0, -390), (40, -340), (80, -380)])
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(6)
        ctx.stroke()
        face(ctx, 0, -280, 0.8, t, 0.4)

    def inside(self, ctx, t):
        ellipse(ctx, 0, -280, 120, 140)
        ctx.set_source_rgb(1, 0.82, 0.25)
        ctx.fill()
        ctx.arc(0, -300, 50, 0, 2 * math.pi)  # embrión con corazón
        ctx.set_source_rgb(1, 0.75, 0.6)
        ctx.fill()
        heart_shape(ctx, 0, -300, 16 * (1 + 0.3 * beat(t, 200)), glow=True)
        for k in range(4):
            a = k * 1.6
            flow_line(ctx, [(0, -300), (math.cos(a) * 110, -280 + math.sin(a) * 120)], t, (1, 0.4, 0.4), 3)


class Campfire(Thing):
    color = (0.6, 0.4, 0.22)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(0, -520)
        ctx.curve_to(150, -350, 180, -100, 0, -80)
        ctx.curve_to(-180, -100, -150, -350, 0, -520)
        ctx.close_path()

    def draw(self, ctx, t):
        glow(ctx, 0, -250, 400, (1, 0.6, 0.2), 0.5)
        for k, (c, s) in enumerate((((1, 0.4, 0.1), 1.0), ((1, 0.7, 0.2), 0.7), ((1, 0.95, 0.5), 0.4))):
            f = 1 + 0.15 * math.sin(t * 15 + k)
            ctx.move_to(10 * math.sin(t * 7 + k), -100 - 420 * s * f)
            ctx.curve_to(150 * s, -350 * s, 180 * s, -100, 0, -80)
            ctx.curve_to(-180 * s, -100, -150 * s, -350 * s, 10 * math.sin(t * 7 + k), -100 - 420 * s * f)
            ctx.set_source_rgb(*c)
            ctx.fill()
        for a in (-0.3, 0.3):
            ctx.save()
            ctx.translate(0, -60)
            ctx.rotate(a)
            rrect(ctx, -220, -30, 220, 30, 28)
            ctx.restore()
            outline(ctx, self.color)
        for k in range(6):
            ph = (t * 0.9 + k / 6) % 1
            ctx.arc(40 * math.sin(k * 2 + t * 3), -400 - ph * 300, 7, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.8, 0.3, 1 - ph)
            ctx.fill()

    def inside(self, ctx, t):
        for k in range(8):
            a = -math.pi / 2 + (k - 3.5) * 0.25
            flow_line(ctx, [(0, -100), (math.cos(a) * 400, -100 + math.sin(a) * 400)], t, (1, 0.5, 0.3), 4)


class Pizza(Thing):
    color = (1.0, 0.82, 0.4)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-260, -600), (260, -600), (0, -80)])

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        rrect(ctx, -280, -650, 280, -580, 30)
        outline(ctx, (0.85, 0.6, 0.3))
        for (x, y) in ((-100, -500), (60, -470), (0, -330), (-30, -560), (120, -550)):
            ctx.arc(x, y, 32, 0, 2 * math.pi)
            outline(ctx, (0.85, 0.2, 0.2), 5)
        k = (t * 0.6) % 1
        ctx.move_to(-40, -200)
        ctx.curve_to(-50, -150 + 60 * k, -30, -100 + 80 * k, -40, -60 + 80 * k)
        ctx.set_source_rgb(1, 0.9, 0.5)
        ctx.set_line_width(14)
        ctx.stroke()
        face(ctx, 0, -440, 0.7, t, 0.6)

    def inside(self, ctx, t):
        bubbles_up(ctx, t, 0, -150, -600, 8, (1, 0.6, 0.3), 12, 120)


class Burger(Thing):
    color = (0.95, 0.7, 0.35)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-240, -520, 480, 440)

    def draw(self, ctx, t):
        rrect(ctx, -230, -200, 230, -90, 40)
        outline(ctx, self.color)
        rrect(ctx, -250, -280, 250, -190, 30)
        outline(ctx, (0.5, 0.3, 0.2))
        ctx.move_to(-260, -300)
        for x in range(-260, 261, 40):
            ctx.line_to(x, -300 + (25 if (x // 40) % 2 else 0))
        ctx.set_source_rgb(0.4, 0.8, 0.35)
        ctx.set_line_width(24)
        ctx.stroke()
        poly(ctx, [(-240, -330), (240, -330), (200, -270), (-200, -270)])
        outline(ctx, (1, 0.85, 0.2), 6)
        ctx.arc(0, -330, 240, math.pi, 2 * math.pi)
        ctx.close_path()
        outline(ctx, self.color)
        for (x, y) in ((-100, -470), (40, -500), (120, -420), (-30, -420)):
            ellipse(ctx, x, y, 12, 7)
            ctx.set_source_rgb(1, 0.97, 0.85)
            ctx.fill()
        face(ctx, 0, -400, 0.8, t, 0.3)

    def inside(self, ctx, t):
        for k, c in enumerate(((1, 0.85, 0.2), (0.4, 0.8, 0.35), (0.55, 0.3, 0.2))):
            ctx.rectangle(-230, -340 + k * 50, 460, 30)
            ctx.set_source_rgb(*c)
            ctx.fill()


class Apple(Thing):
    color = (0.92, 0.25, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(0, -520)
        ctx.curve_to(-120, -600, -300, -520, -260, -300)
        ctx.curve_to(-230, -100, -80, -60, 0, -100)
        ctx.curve_to(80, -60, 230, -100, 260, -300)
        ctx.curve_to(300, -520, 120, -600, 0, -520)
        ctx.close_path()

    def draw(self, ctx, t):
        ctx.move_to(0, -520)
        ctx.line_to(20, -620)
        ctx.set_source_rgb(0.4, 0.25, 0.15)
        ctx.set_line_width(16)
        ctx.stroke()
        ctx.save()
        ctx.translate(30, -600)
        ctx.rotate(-0.5 + 0.1 * math.sin(t * 2))
        ellipse(ctx, 60, 0, 70, 30)
        ctx.restore()
        outline(ctx, (0.35, 0.75, 0.35), 7)
        self.body(ctx, t)
        outline(ctx, self.color)
        ellipse(ctx, -130, -420, 30, 60)
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.fill()
        face(ctx, 0, -340, 0.9, t, 0.5)

    def inside(self, ctx, t):
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        ctx.rectangle(-300, -600, 600, 600)
        ctx.set_source_rgba(1, 0.97, 0.85, 0.9)
        ctx.fill()
        ctx.restore()
        for (x, y, a) in ((-30, -340, 0.3), (30, -340, -0.3), (0, -280, 0)):
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(a)
            ellipse(ctx, 0, 0, 16, 28)
            ctx.restore()
            ctx.set_source_rgb(0.4, 0.25, 0.15)
            ctx.fill()


class Cake(Thing):
    color = (1.0, 0.75, 0.82)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-250, -420, 500, 400)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.move_to(-250, -400)
        for x in range(-250, 251, 50):
            ctx.line_to(x, -400 + (40 if (x // 50) % 2 else 0))
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(24)
        ctx.stroke()
        for x in (-120, 0, 120):
            ctx.rectangle(x - 12, -520, 24, 100)
            outline(ctx, (0.5, 0.75, 1), 5)
            f = 1 + 0.2 * math.sin(t * 14 + x)
            ctx.move_to(x, -520 - 50 * f)
            ctx.curve_to(x + 20, -530, x + 12, -515, x, -515)
            ctx.curve_to(x - 12, -515, x - 20, -530, x, -520 - 50 * f)
            ctx.set_source_rgb(1, 0.6, 0.15)
            ctx.fill()
        face(ctx, 0, -230, 0.9, t, 0.7)

    def inside(self, ctx, t):
        for k, c in enumerate(((0.55, 0.3, 0.2), (1, 0.95, 0.85), (0.95, 0.35, 0.45), (1, 0.95, 0.85), (0.55, 0.3, 0.2))):
            ctx.rectangle(-240, -400 + k * 76, 480, 70)
            ctx.set_source_rgb(*c)
            ctx.fill()


class Trophy(Thing):
    color = (1.0, 0.8, 0.2)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-190, -650)
        ctx.line_to(190, -650)
        ctx.curve_to(190, -400, 80, -330, 40, -320)
        ctx.line_to(40, -200)
        ctx.line_to(-40, -200)
        ctx.line_to(-40, -320)
        ctx.curve_to(-80, -330, -190, -400, -190, -650)
        ctx.close_path()

    def draw(self, ctx, t):
        for sx in (-1, 1):
            ctx.arc(sx * 200, -560, 70, -math.pi / 2 if sx > 0 else math.pi / 2, math.pi / 2 if sx > 0 else 3 * math.pi / 2)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(40)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*self.color)
            ctx.set_line_width(26)
            ctx.stroke()
        rrect(ctx, -150, -210, 150, -80, 16)
        outline(ctx, (0.5, 0.32, 0.2))
        self.body(ctx, t)
        outline(ctx, self.color)
        s = abs(math.sin(t * 2))
        ctx.save()
        ctx.translate(-90, -560)
        ctx.scale(s, s)
        poly(ctx, [(0, -40), (10, -10), (40, 0), (10, 10), (0, 40), (-10, 10), (-40, 0), (-10, -10)])
        ctx.restore()
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(110)
        ctx.move_to(-35, -440)
        ctx.text_path("1")
        outline(ctx, (1, 0.95, 0.6), 6)

    def inside(self, ctx, t):
        glow(ctx, 0, -500, 180, (1, 1, 0.6), 0.7)


class Ball(Thing):
    color = (1, 1, 1)

    def __init__(self, kind="football"):
        self.kind = kind
        self.color = (1, 1, 1) if kind == "football" else (1.0, 0.55, 0.15)

    def _y(self, t):
        return -200 - abs(math.sin(t * 3)) * 300

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, self._y(t), 180, 0, 2 * math.pi)

    def draw(self, ctx, t):
        y = self._y(t)
        ctx.save()
        ctx.translate(0, -10)
        ctx.scale(1, 0.2)
        ctx.arc(0, 0, 160 * (1 - (y + 200) / -600), 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.15)
        ctx.fill()
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.save()
        ctx.translate(0, y)
        ctx.rotate(t * 3)
        if self.kind == "football":
            for k in range(6):
                a = k * math.pi / 3
                r = 0 if k == 0 else 110
                cx, cy = (0, 0) if k == 0 else (math.cos(a) * r, math.sin(a) * r)
                for j in range(5):
                    b = -math.pi / 2 + j * 2 * math.pi / 5
                    (ctx.move_to if j == 0 else ctx.line_to)(cx + math.cos(b) * 45, cy + math.sin(b) * 45)
                ctx.close_path()
                ctx.set_source_rgb(*INK)
                ctx.fill()
        else:
            ctx.move_to(-180, 0)
            ctx.line_to(180, 0)
            ctx.move_to(0, -180)
            ctx.line_to(0, 180)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(8)
            ctx.stroke()
            for sx in (-1, 1):
                ctx.arc(sx * 260, 0, 200, math.pi * 0.8, math.pi * 1.2) if sx > 0 else ctx.arc(sx * 260, 0, 200, -0.2 * math.pi, 0.2 * math.pi)
                ctx.stroke()
        ctx.restore()

    def inside(self, ctx, t):
        y = self._y(t)
        for k in range(10):
            a = k * 0.63 + t * 2
            ctx.arc(math.cos(a) * 110, y + math.sin(a) * 110, 12, 0, 2 * math.pi)
            ctx.set_source_rgba(0.7, 0.95, 1, 0.9)  # aire a presión
            ctx.fill()


class Guitar(Thing):
    color = (0.85, 0.5, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -260, 170, 0, 2 * math.pi)
        ctx.new_sub_path()
        ctx.arc(0, -450, 130, 0, 2 * math.pi)

    def draw(self, ctx, t):
        ctx.rectangle(-28, -880, 56, 440)
        outline(ctx, (0.45, 0.3, 0.18))
        rrect(ctx, -50, -950, 50, -860, 16)
        outline(ctx, (0.45, 0.3, 0.18))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.arc(0, -330, 55, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        for k in range(4):
            x = -18 + k * 12
            ctx.move_to(x, -880)
            for j in range(20):
                y = -880 + j * 37
                ctx.line_to(x + 4 * math.sin(t * 40 + j) * (j % 2), y)
            ctx.set_source_rgb(0.95, 0.95, 0.9)
            ctx.set_line_width(3)
            ctx.stroke()
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1
            ctx.arc(0, -330, 80 + ph * 200, -0.5, 0.5)
            ctx.set_source_rgba(0.5, 0.8, 1, 1 - ph)
            ctx.set_line_width(6)
            ctx.stroke()

    def inside(self, ctx, t):
        for k in range(4):
            ph = (t * 1.5 + k / 4) % 1
            ctx.arc(0, -300, 30 + ph * 130, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.6, 1 - ph)
            ctx.set_line_width(5)
            ctx.stroke()


class Moai(Thing):
    color = (0.6, 0.58, 0.55)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-160, -760), (150, -760), (190, -320), (220, 0), (-220, 0), (-200, -320)])

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(-180, -760, 340, 70)
        ctx.set_source_rgb(*shade(self.color, 0.85))
        ctx.fill()
        poly(ctx, [(-40, -650), (40, -650), (70, -440), (-70, -440)])
        outline(ctx, shade(self.color, 0.9), 7)
        blink = ((t + 0.4) % 4) < 0.15
        for sx in (-1, 1):
            ctx.rectangle(sx * 95 - 45, -640, 90, 18 if blink else 40)
            ctx.set_source_rgb(*INK)
            ctx.fill()
        ctx.rectangle(-70, -380, 140, 26)
        ctx.fill()

    def inside(self, ctx, t):
        for k in range(12):
            ctx.arc(-150 + (k * 67) % 300, -100 - (k * 61) % 600, 20, 0, 2 * math.pi)
            ctx.set_source_rgba(0.8, 0.8, 0.85, 0.7)
            ctx.fill()


class Eiffel(Thing):
    color = (0.6, 0.42, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-260, 0), (-40, -800), (40, -800), (260, 0)])

    def draw(self, ctx, t):
        ctx.set_source_rgb(*self.color)
        for side in (-1, 1):
            ctx.move_to(side * 260, 0)
            ctx.curve_to(side * 130, -250, side * 60, -500, side * 15, -820)
        ctx.set_line_width(26)
        ctx.stroke()
        ctx.move_to(-150, 0)
        ctx.arc(0, 0, 150, math.pi, 2 * math.pi)
        ctx.set_line_width(16)
        ctx.stroke()
        for (y, w) in ((-260, 150), (-520, 70)):
            ctx.rectangle(-w, y - 15, 2 * w, 30)
            outline(ctx, self.color, 6)
        for k in range(14):
            y = -40 - k * 55
            w = 250 * (1 - k / 15) ** 1.6
            ctx.move_to(-w, y)
            ctx.line_to(w, y - 50)
            ctx.move_to(w, y)
            ctx.line_to(-w, y - 50)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.arc(0, -840, 18, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.9 * abs(math.sin(t * 3)) + 0.1, 0.3)
        ctx.fill()

    def inside(self, ctx, t):
        y = -40 - 500 * (0.5 + 0.5 * math.sin(t * 0.8))
        ctx.rectangle(-20, y, 40, 40)
        ctx.set_source_rgb(1, 0.85, 0.3)
        ctx.fill()


THINGS = {
    "rocket": Rocket(), "ufo": UFO(), "sun": Sun(), "moon": Moon(), "saturn": Saturn(), "black_hole": BlackHole(),
    "comet": Comet(), "satellite": Satellite(), "car": Car(), "plane": Plane(), "ship": Ship(), "submarine": Submarine(),
    "train": Train(), "house": House(), "skyscraper": Skyscraper(), "tree": Tree(), "mushroom": Mushroom(),
    "cactus": Cactus(), "flower": Flower(), "iceberg": Iceberg(), "tornado": Tornado(), "storm_cloud": StormCloud(),
    "lightbulb": LightBulb(), "phone": Phone(), "computer": Computer(), "battery": Battery(), "magnet": Magnet(),
    "money_bag": MoneyBag(), "diamond": Diamond(), "treasure": Treasure(), "clock": Clock(), "hourglass": Hourglass(),
    "book": Book(), "telescope": Telescope(), "bomb": Bomb(), "heart_organ": HeartOrgan(), "brain_organ": BrainOrgan(),
    "lungs_organ": LungsOrgan(), "stomach_organ": StomachOrgan(), "tooth": Tooth(), "eye_organ": EyeOrgan(),
    "bacteria": Bacteria(), "virus_big": VirusBig(), "cell": Cell(), "dna": DNABig(), "atom": AtomBig(), "egg": Egg(),
    "campfire": Campfire(), "pizza": Pizza(), "burger": Burger(), "apple": Apple(), "cake": Cake(), "trophy": Trophy(),
    "football": Ball("football"), "basketball": Ball("basketball"), "guitar": Guitar(), "moai": Moai(),
    "eiffel_tower": Eiffel(),
}

THING_PARTS = {k: {"body": (0, -400), "core": (0, -400), "inside": (0, -400)} for k in THINGS}
THING_PARTS["rocket"].update(engine=(0, -260), tank=(0, -360))
THING_PARTS["tree"].update(roots=(0, -30), leaves=(0, -560))
THING_PARTS["iceberg"].update(underwater=(0, -150))
