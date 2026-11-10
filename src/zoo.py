"""Animales generados con plantillas paramétricas (mismo estilo que los monigotes).

Cada plantilla (cuadrúpedo, ave, pez, insecto...) dibuja muchas especies cambiando
parámetros. Todas miran a la izquierda (hacia el narrador), tienen partes que se mueven
y un interior para el modo rayos X.
"""
import math

import cairo

from src.creatures import (INK, Creature, beat, bones, ellipse, eye, flow_line, heart_shape, outline, shade,
                           smile, tentacle)


def _limb(ctx, x1, y1, x2, y2, w, color):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(w + 14)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*color)
    ctx.set_line_width(w)
    ctx.stroke()


def _poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def tube_path(ctx, pts, w0, w1):
    """Contorno de un tubo que sigue una línea (para recortar serpientes y anguilas)."""
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[min(i + 1, n - 1)]
        b = pts[max(i - 1, 0)]
        dx, dy = a[0] - b[0], a[1] - b[1]
        d = math.hypot(dx, dy) or 1
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x - dy / d * w, y + dx / d * w))
        right.append((x + dy / d * w, y - dx / d * w))
    ctx.new_path()
    ctx.move_to(*left[0])
    for q in left[1:]:
        ctx.line_to(*q)
    ctx.arc(pts[-1][0], pts[-1][1], w1 / 2, 0, 2 * math.pi) if False else None
    for q in reversed(right):
        ctx.line_to(*q)
    ctx.close_path()


def stomach(ctx, x, y, r, t):
    ellipse(ctx, x, y, r * 1.2, r * 0.8)
    ctx.set_source_rgba(1.0, 0.75, 0.5, 0.9)
    ctx.fill()
    for k in range(3):
        ph = (t * 0.8 + k / 3) % 1
        ctx.arc(x - r * 0.5 + k * r * 0.5, y + r * 0.3 - ph * r * 0.6, 5, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.8, 1 - ph)
        ctx.fill()


# ================================================================ CUADRÚPEDOS
class Quadruped(Creature):
    def __init__(self, **p):
        d = dict(color=(0.8, 0.6, 0.4), belly=None, bx=40, by=-290, brx=190, bry=110, leg=170, legw=34,
                 head=(-170, -400, 85), ears="round", snout="dog", tail="thin", pattern=None, extras=(),
                 neck=None, walk=True, nose=INK, pcolor=INK, bpm=80)
        d.update(p)
        self.p = d
        self.color = d["color"]

    def body(self, ctx, t):
        p = self.p
        ctx.new_path()
        ellipse(ctx, p["bx"], p["by"], p["brx"], p["bry"])
        hx, hy, hr = p["head"]
        ctx.new_sub_path()
        ellipse(ctx, hx, hy, hr * 1.05, hr)
        if p["neck"]:
            nx, ny = p["neck"]
            ctx.new_sub_path()
            _poly(ctx, [(p["bx"] - p["brx"] * 0.75, p["by"] - 40), (nx + 45, ny), (nx - 45, ny),
                        (p["bx"] - p["brx"] * 0.95, p["by"] + 30)])

    def draw(self, ctx, t):
        p = self.p
        c, belly = p["color"], p["belly"] or shade(p["color"], 1.15)
        bx, by, brx, bry = p["bx"], p["by"], p["brx"], p["bry"]
        hx, hy, hr = p["head"]
        sw = math.sin(t * 5) if p["walk"] else 0
        legy = by + bry * 0.55
        xs = [bx - brx * 0.62, bx - brx * 0.35, bx + brx * 0.42, bx + brx * 0.68]
        # patas traseras (las del fondo, más oscuras)
        for k, x in enumerate(xs):
            if k % 2 == 1:
                ph = sw * (1 if k < 2 else -1)
                _limb(ctx, x, legy, x + 22 * ph, -8, p["legw"], shade(c, 0.85))
        # cola
        tx, ty = bx + brx * 0.92, by - bry * 0.3
        wag = math.sin(t * (7 if p["tail"] in ("thin", "bushy") else 3))
        if p["tail"] == "bushy":
            ctx.move_to(tx, ty)
            ctx.curve_to(tx + 110, ty - 40, tx + 150 + 20 * wag, ty - 150, tx + 120 + 30 * wag, ty - 200)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(70)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(54)
            ctx.stroke()
        elif p["tail"] == "curly":
            ctx.arc(tx + 35, ty, 26, 0, 2 * math.pi * (0.7 + 0.2 * wag))
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(14)
            ctx.stroke()
        elif p["tail"] != "none":
            length = {"short": 50, "tuft": 140, "thin": 150, "long": 220}.get(p["tail"], 150)
            ex, ey = tx + length * 0.7, ty + length * 0.5 + 30 * wag
            ctx.move_to(tx, ty)
            ctx.curve_to(tx + length * 0.4, ty - 20, ex - 20, ey - 40, ex, ey)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(22)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(12)
            ctx.stroke()
            if p["tail"] == "tuft":
                ctx.arc(ex, ey, 22, 0, 2 * math.pi)
                outline(ctx, shade(c, 0.6), 7)
        # cuello largo
        if p["neck"]:
            nx, ny = p["neck"]
            sway = 8 * math.sin(t * 1.5)
            _poly(ctx, [(bx - brx * 0.75, by - 40), (nx + 45 + sway, ny), (nx - 45 + sway, ny),
                        (bx - brx * 0.95, by + 30)])
            outline(ctx, c)
        # joroba
        if "hump" in p["extras"]:
            ellipse(ctx, bx + 20, by - bry * 0.85, brx * 0.45, bry * 0.6)
            outline(ctx, c)
        # cuerpo
        ellipse(ctx, bx, by, brx, bry)
        outline(ctx, c)
        ctx.save()
        ellipse(ctx, bx, by, brx, bry)
        ctx.clip()
        ellipse(ctx, bx, by + bry * 0.75, brx * 0.8, bry * 0.45)
        ctx.set_source_rgb(*belly)
        ctx.fill()
        self._pattern(ctx, bx - brx, by - bry, brx * 2, bry * 2, p["pattern"], p["pcolor"])
        ctx.restore()
        # patas delanteras
        for k, x in enumerate(xs):
            if k % 2 == 0:
                ph = -sw * (1 if k < 2 else -1)
                _limb(ctx, x, legy, x + 22 * ph, -8, p["legw"], c)
                if "hooves" in p["extras"]:
                    ctx.rectangle(x + 22 * ph - p["legw"] / 2 - 4, -26, p["legw"] + 8, 22)
                    outline(ctx, (0.25, 0.2, 0.18), 5)
        # melena
        if "mane" in p["extras"]:
            for k in range(14):
                a = k * 2 * math.pi / 14 + 0.05 * math.sin(t * 3 + k)
                ctx.new_sub_path()
                ctx.arc(hx + math.cos(a) * hr * 0.95, hy + math.sin(a) * hr * 0.95, hr * 0.42, 0, 2 * math.pi)
            outline(ctx, shade(c, 0.7), 8)
        # cuernos / astas
        if "horns" in p["extras"]:
            for sx in (-1, 1):
                ctx.move_to(hx + sx * hr * 0.45, hy - hr * 0.7)
                ctx.curve_to(hx + sx * hr * 0.8, hy - hr * 1.2, hx + sx * hr * 1.1, hy - hr * 1.3, hx + sx * hr * 1.2,
                             hy - hr * 1.6)
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(26)
                ctx.stroke_preserve()
                ctx.set_source_rgb(0.95, 0.9, 0.8)
                ctx.set_line_width(16)
                ctx.stroke()
        if "antlers" in p["extras"]:
            ctx.set_source_rgb(0.55, 0.38, 0.22)
            ctx.set_line_width(14)
            for sx in (-1, 1):
                x0, y0 = hx + sx * hr * 0.4, hy - hr * 0.8
                ctx.move_to(x0, y0)
                ctx.line_to(x0 + sx * 50, y0 - 150)
                ctx.move_to(x0 + sx * 20, y0 - 60)
                ctx.line_to(x0 + sx * 90, y0 - 100)
                ctx.move_to(x0 + sx * 38, y0 - 110)
                ctx.line_to(x0 - sx * 10, y0 - 170)
            ctx.stroke()
        if "ossicones" in p["extras"]:
            for sx in (-1, 1):
                _limb(ctx, hx + sx * 25, hy - hr * 0.8, hx + sx * 30, hy - hr * 1.4, 10, c)
                ctx.arc(hx + sx * 30, hy - hr * 1.45, 14, 0, 2 * math.pi)
                outline(ctx, shade(c, 0.6), 5)
        # orejas
        self._ears(ctx, hx, hy, hr, t, p["ears"], c)
        # cabeza
        ellipse(ctx, hx, hy, hr * 1.05, hr)
        outline(ctx, c)
        ctx.save()
        ellipse(ctx, hx, hy, hr * 1.05, hr)
        ctx.clip()
        if p["pattern"] in ("stripes", "spots"):
            self._pattern(ctx, hx - hr, hy - hr, hr * 2, hr * 2, p["pattern"], p["pcolor"])
        if p["pattern"] == "panda":
            for sx in (-1, 1):
                ellipse(ctx, hx - 20 + sx * 35, hy - 10, 28, 36)
                ctx.set_source_rgb(*INK)
                ctx.fill()
        ctx.restore()
        self._snout(ctx, hx, hy, hr, t, p["snout"], c, belly, p["nose"])
        eye(ctx, hx - hr * 0.35, hy - hr * 0.25, hr * 0.2, t, 0.37 + (id(self) % 7) * 0.4)
        eye(ctx, hx + hr * 0.2, hy - hr * 0.25, hr * 0.2, t, 0.37 + (id(self) % 7) * 0.4)
        if "unicorn_horn" in p["extras"]:
            _poly(ctx, [(hx - hr * 0.25, hy - hr * 0.8), (hx - hr * 0.55, hy - hr * 1.9), (hx + hr * 0.05, hy - hr * 0.85)])
            outline(ctx, (1.0, 0.85, 0.3), 7)
        if "horn" in p["extras"]:  # rinoceronte
            _poly(ctx, [(hx - hr * 0.85, hy + hr * 0.05), (hx - hr * 1.25, hy - hr * 0.75), (hx - hr * 0.55, hy - hr * 0.1)])
            outline(ctx, (0.92, 0.88, 0.8), 7)
        if "tusks" in p["extras"]:
            ctx.move_to(hx - hr * 0.6, hy + hr * 0.55)
            ctx.curve_to(hx - hr * 0.9, hy + hr * 1.0, hx - hr * 1.3, hy + hr * 1.0, hx - hr * 1.4, hy + hr * 0.7)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(26)
            ctx.stroke_preserve()
            ctx.set_source_rgb(1, 0.98, 0.9)
            ctx.set_line_width(16)
            ctx.stroke()

    def _pattern(self, ctx, x, y, w, h, kind, col):
        if kind == "stripes":
            ctx.set_source_rgb(*col)
            for k in range(9):
                xx = x + k * w / 8
                ctx.move_to(xx, y)
                ctx.curve_to(xx + 25, y + h * 0.3, xx - 25, y + h * 0.6, xx + 10, y + h)
                ctx.set_line_width(w / 30)
            ctx.stroke()
        elif kind == "spots":
            for k in range(16):
                ctx.new_sub_path()
                ctx.arc(x + (k * 0.618 % 1) * w, y + (k * 0.37 % 1) * h, w * 0.045 + (k % 3) * 4, 0, 2 * math.pi)
            ctx.set_source_rgb(*col)
            ctx.fill()
        elif kind == "patches":
            for (a, b, r) in ((0.3, 0.35, 0.16), (0.7, 0.5, 0.2), (0.5, 0.15, 0.1)):
                ellipse(ctx, x + a * w, y + b * h, r * w, r * w * 0.7)
                ctx.set_source_rgb(*col)
                ctx.fill()
        elif kind == "giraffe":
            for k in range(14):
                cx, cy = x + (k * 0.618 % 1) * w, y + (k * 0.41 % 1) * h
                _poly(ctx, [(cx - 30, cy - 20), (cx + 10, cy - 34), (cx + 34, cy), (cx + 10, cy + 30), (cx - 28, cy + 18)])
                ctx.set_source_rgb(*col)
                ctx.fill()

    def _ears(self, ctx, hx, hy, hr, t, kind, c):
        f = 0.08 * math.sin(t * 4)
        if kind == "pointy":
            for sx in (-1, 1):
                _poly(ctx, [(hx + sx * hr * 0.2, hy - hr * 0.7), (hx + sx * hr * 0.75, hy - hr * (1.55 + f)),
                            (hx + sx * hr * 0.85, hy - hr * 0.45)])
                outline(ctx, c)
        elif kind == "floppy":
            for sx in (-1, 1):
                ctx.save()
                ctx.translate(hx + sx * hr * 0.7, hy - hr * 0.4)
                ctx.rotate(sx * (0.3 + f))
                ellipse(ctx, 0, hr * 0.45, hr * 0.3, hr * 0.6)
                ctx.restore()
                outline(ctx, shade(c, 0.75))
        elif kind == "big":  # elefante
            ctx.save()
            ctx.translate(hx + hr * 0.6, hy)
            ctx.scale(1 + f, 1)
            ellipse(ctx, hr * 0.4, hr * 0.1, hr * 0.95, hr * 1.1)
            ctx.restore()
            outline(ctx, shade(c, 0.9))
        elif kind == "long":  # conejo
            for sx in (-1, 1):
                ctx.save()
                ctx.translate(hx + sx * hr * 0.35, hy - hr * 0.8)
                ctx.rotate(sx * 0.15 + f)
                ellipse(ctx, 0, -hr * 0.9, hr * 0.28, hr * 1.0)
                ctx.restore()
                outline(ctx, c)
        elif kind == "small":
            for sx in (-1, 1):
                ctx.arc(hx + sx * hr * 0.6, hy - hr * 0.8, hr * 0.22, 0, 2 * math.pi)
                outline(ctx, c)
        elif kind != "none":  # round
            for sx in (-1, 1):
                ctx.arc(hx + sx * hr * 0.65, hy - hr * 0.75, hr * 0.32, 0, 2 * math.pi)
                outline(ctx, c)

    def _snout(self, ctx, hx, hy, hr, t, kind, c, belly, nose):
        chew = 0.5 + 0.5 * math.sin(t * 4)
        if kind == "trunk":
            sw = 0.4 * math.sin(t * 2)
            pts = []
            for j in range(11):
                s = j / 10
                pts.append((hx - hr * 0.7 - s * hr * 0.6 + 30 * math.sin(s * 3 + sw) * s,
                            hy + hr * 0.1 + s * hr * 1.6 - (s ** 3) * hr * 0.9 * (1 + sw)))
            tentacle(ctx, pts, 70, 40, c)
            return
        if kind == "long":  # caballo
            ellipse(ctx, hx - hr * 0.75, hy + hr * 0.35, hr * 0.6, hr * 0.42)
            outline(ctx, shade(c, 1.1))
            for sx in (-0.95, -0.65):
                ctx.arc(hx + hr * sx, hy + hr * 0.35, 6, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.fill()
            return
        if kind == "pig":
            ellipse(ctx, hx - hr * 0.8, hy + hr * 0.25, hr * 0.32, hr * 0.26)
            outline(ctx, shade(c, 1.05))
            for dy in (-8, 8):
                ellipse(ctx, hx - hr * 0.8, hy + hr * 0.25 + dy, 6, 5)
                ctx.set_source_rgb(*INK)
                ctx.fill()
            return
        if kind == "hippo":
            ellipse(ctx, hx - hr * 0.55, hy + hr * 0.4, hr * 0.8, hr * 0.55)
            outline(ctx, shade(c, 1.05))
            return
        if kind == "mouse":
            _poly(ctx, [(hx - hr * 0.6, hy - hr * 0.2), (hx - hr * 1.35, hy + hr * 0.25), (hx - hr * 0.5, hy + hr * 0.5)])
            outline(ctx, c)
            ctx.arc(hx - hr * 1.35, hy + hr * 0.25, 10, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.5, 0.6)
            ctx.fill()
            return
        # perro / gato / oso / vaca
        sx = {"dog": 0.95, "cat": 0.6, "bear": 0.8, "cow": 0.7}.get(kind, 0.8)
        ellipse(ctx, hx - hr * sx * 0.7, hy + hr * 0.3, hr * sx * 0.55, hr * 0.38)
        outline(ctx, belly)
        ellipse(ctx, hx - hr * sx * 1.15, hy + hr * 0.15, hr * 0.17, hr * 0.13)
        ctx.set_source_rgb(*nose)
        ctx.fill()
        ctx.move_to(hx - hr * sx * 0.95, hy + hr * 0.5)
        ctx.curve_to(hx - hr * sx * 0.8, hy + hr * (0.55 + 0.1 * chew), hx - hr * sx * 0.55, hy + hr * 0.55,
                     hx - hr * sx * 0.45, hy + hr * 0.45)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(6)
        ctx.stroke()

    def inside(self, ctx, t):
        p = self.p
        bx, by, brx, bry = p["bx"], p["by"], p["brx"], p["bry"]
        hx, hy, hr = p["head"]
        bones(ctx, bx + brx * 0.8, by - bry * 0.3, bx - brx * 0.8, by - bry * 0.35, 12)
        for k in range(7):
            x = bx - brx * 0.5 + k * brx * 0.16
            ctx.move_to(x, by - bry * 0.33)
            ctx.curve_to(x - 15, by, x - 5, by + bry * 0.4, x + 10, by + bry * 0.55)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(7)
            ctx.stroke()
        ellipse(ctx, hx, hy, hr * 0.8, hr * 0.75)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(9)
        ctx.stroke()
        ellipse(ctx, hx + hr * 0.1, hy - hr * 0.15, hr * 0.45, hr * 0.32)
        ctx.set_source_rgba(1.0, 0.68, 0.8, 0.9)
        ctx.fill()
        heart_shape(ctx, bx - brx * 0.35, by + bry * 0.05, bry * 0.32 * (1 + 0.2 * beat(t, p["bpm"])), glow=True)
        stomach(ctx, bx + brx * 0.2, by + bry * 0.2, bry * 0.35, t)
        flow_line(ctx, [(bx - brx * 0.35, by), (bx - brx * 0.7, by - bry * 0.4), (hx + hr * 0.3, hy + hr * 0.6)],
                  t, (1.0, 0.35, 0.4), 6)


# ================================================================ AVES
class BirdT(Creature):
    def __init__(self, **p):
        d = dict(color=(0.4, 0.7, 0.95), belly=(0.95, 0.95, 0.95), size=1.0, beak="short", beakc=(1.0, 0.7, 0.15),
                 legs="short", legc=(1.0, 0.65, 0.2), fly=True, crest=False, bigeyes=False, tail="fan",
                 neck=0, extras=(), y=-340, bpm=200)
        d.update(p)
        self.p = d
        self.color = d["color"]
        self.float_ = d["fly"]

    def _geo(self):
        p = self.p
        s = p["size"]
        return 0, p["y"], 150 * s, 125 * s

    def body(self, ctx, t):
        bx, by, rx, ry = self._geo()
        ctx.new_path()
        ellipse(ctx, bx, by, rx, ry)

    def draw(self, ctx, t):
        p = self.p
        c = p["color"]
        bx, by, rx, ry = self._geo()
        flap = math.sin(t * (9 if p["fly"] else 2.5))
        # patas
        if p["legs"] != "none":
            L = {"short": 90, "long": 330}.get(p["legs"], 90)
            for k, sx in enumerate((-30, 30)):
                kn = 20 * math.sin(t * 4 + k) if p["legs"] == "long" else 0
                ctx.move_to(bx + sx, by + ry * 0.8)
                ctx.line_to(bx + sx + kn, by + ry * 0.8 + L * 0.55)
                ctx.line_to(bx + sx, by + ry * 0.8 + L)
                ctx.line_to(bx + sx - 30, by + ry * 0.8 + L + 4)
                ctx.set_source_rgb(*p["legc"])
                ctx.set_line_width(12)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke()
        # cola
        if p["tail"] == "fan":
            _poly(ctx, [(bx + rx * 0.85, by - 10), (bx + rx * 1.7, by - ry * 0.6 + 10 * flap), (bx + rx * 1.65, by + ry * 0.3)])
            outline(ctx, shade(c, 0.8))
        elif p["tail"] == "long":
            ctx.move_to(bx + rx * 0.8, by)
            ctx.curve_to(bx + rx * 1.6, by + 40, bx + rx * 2.2, by + 140 + 20 * flap, bx + rx * 2.4, by + 220)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(48)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*shade(c, 0.9))
            ctx.set_line_width(34)
            ctx.stroke()
        # cuello largo
        hx, hy = bx - rx * 0.75, by - ry * 0.75
        if p["neck"]:
            n = p["neck"]
            sway = 12 * math.sin(t * 2)
            ctx.move_to(bx - rx * 0.5, by - ry * 0.3)
            ctx.curve_to(bx - rx * 0.9, by - n * 0.4, bx - rx * 0.6 + sway, by - n * 0.8, bx - rx * 0.7 + sway, by - n)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(64)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(48)
            ctx.stroke()
            hx, hy = bx - rx * 0.7 + sway, by - n
        # cuerpo
        ellipse(ctx, bx, by, rx, ry)
        outline(ctx, c)
        ctx.save()
        ellipse(ctx, bx, by, rx, ry)
        ctx.clip()
        ellipse(ctx, bx - rx * 0.25, by + ry * 0.35, rx * 0.7, ry * 0.7)
        ctx.set_source_rgb(*p["belly"])
        ctx.fill()
        ctx.restore()
        # ala
        ctx.save()
        ctx.translate(bx + rx * 0.1, by - ry * 0.2)
        ctx.rotate(-0.9 * flap if p["fly"] else 0.25 + 0.15 * flap)
        if p["fly"]:
            ctx.move_to(0, 0)
            ctx.curve_to(rx * 0.6, -ry * 0.6, rx * 1.4, -ry * 0.6, rx * 1.6, -ry * 0.1)
            ctx.curve_to(rx * 1.0, ry * 0.1, rx * 0.5, ry * 0.3, 0, 0)
        else:
            ellipse(ctx, rx * 0.2, ry * 0.45, rx * 0.25, ry * 0.6)
        ctx.restore()
        outline(ctx, shade(c, 0.82))
        # cabeza
        hr = rx * (0.55 if p["neck"] else 0.62)
        if p["crest"]:
            for k in range(3):
                _poly(ctx, [(hx - 10 + k * 25, hy - hr * 0.7), (hx + 5 + k * 35, hy - hr * 1.6 + 10 * math.sin(t * 5 + k)),
                            (hx + 30 + k * 25, hy - hr * 0.6)])
                outline(ctx, (1.0, 0.5, 0.2) if k % 2 else (1.0, 0.85, 0.2), 6)
        if "ears" in p["extras"]:  # búho
            for sx in (-1, 1):
                _poly(ctx, [(hx + sx * hr * 0.3, hy - hr * 0.7), (hx + sx * hr * 0.75, hy - hr * 1.35), (hx + sx * hr * 0.8, hy - hr * 0.5)])
                outline(ctx, c)
        ctx.arc(hx, hy, hr, 0, 2 * math.pi)
        outline(ctx, c)
        if "comb" in p["extras"]:  # gallina
            for k in range(3):
                ctx.arc(hx - 20 + k * 25, hy - hr * 0.95, 20, 0, 2 * math.pi)
                outline(ctx, (0.95, 0.2, 0.2), 6)
        if "mask" in p["extras"]:  # pingüino: cara blanca
            ellipse(ctx, hx - hr * 0.1, hy + hr * 0.15, hr * 0.65, hr * 0.65)
            ctx.set_source_rgb(*p["belly"])
            ctx.fill()
        er = hr * (0.4 if p["bigeyes"] else 0.24)
        if p["bigeyes"]:
            eye(ctx, hx - hr * 0.42, hy - hr * 0.05, er, t, 0.4)
            eye(ctx, hx + hr * 0.42, hy - hr * 0.05, er, t, 0.4)
        else:
            eye(ctx, hx - hr * 0.3, hy - hr * 0.2, er, t, 0.6)
        # pico
        op = max(0, math.sin(t * 3)) * 0.25
        b = p["beak"]
        bc = p["beakc"]
        if b == "long":
            _poly(ctx, [(hx - hr * 0.8, hy - 12), (hx - hr * 2.6, hy + 10), (hx - hr * 0.8, hy + 22)])
        elif b == "hook":
            ctx.move_to(hx - hr * 0.8, hy - 20)
            ctx.curve_to(hx - hr * 1.6, hy - 30, hx - hr * 1.6, hy + 30, hx - hr * 1.3, hy + 45)
            ctx.line_to(hx - hr * 0.8, hy + 22)
            ctx.close_path()
        elif b == "flat":  # pato
            ellipse(ctx, hx - hr * 1.15, hy + hr * 0.15, hr * 0.55, hr * 0.2)
        elif b == "big":  # tucán
            ctx.move_to(hx - hr * 0.7, hy - hr * 0.4)
            ctx.curve_to(hx - hr * 2.0, hy - hr * 0.5, hx - hr * 2.6, hy + hr * 0.2, hx - hr * 2.3, hy + hr * 0.4)
            ctx.line_to(hx - hr * 0.7, hy + hr * 0.4)
            ctx.close_path()
        elif b == "bent":  # flamenco
            ctx.move_to(hx - hr * 0.7, hy - 15)
            ctx.line_to(hx - hr * 1.5, hy)
            ctx.line_to(hx - hr * 1.6, hy + 45)
            ctx.line_to(hx - hr * 1.35, hy + 20)
            ctx.line_to(hx - hr * 0.7, hy + 22)
            ctx.close_path()
        else:
            _poly(ctx, [(hx - hr * 0.8, hy - 18 - op * 20), (hx - hr * 1.5, hy + 5), (hx - hr * 0.8, hy + 26 + op * 20)])
        outline(ctx, bc, 7)

    def inside(self, ctx, t):
        bx, by, rx, ry = self._geo()
        bones(ctx, bx - rx * 0.6, by - ry * 0.2, bx + rx * 0.7, by - ry * 0.1, 10)
        for k in range(5):
            x = bx - rx * 0.4 + k * rx * 0.2
            ctx.move_to(x, by - ry * 0.2)
            ctx.curve_to(x - 10, by + ry * 0.2, x, by + ry * 0.4, x + 10, by + ry * 0.55)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(6)
            ctx.stroke()
        heart_shape(ctx, bx - rx * 0.3, by + ry * 0.1, ry * 0.25 * (1 + 0.3 * beat(t, self.p["bpm"])), glow=True)
        for k in range(3):
            ellipse(ctx, bx + rx * 0.15 + k * 30, by + ry * 0.35, 22, 15 * (1 + 0.2 * math.sin(t * 6 + k)))
            ctx.set_source_rgba(0.8, 0.95, 1, 0.8)
            ctx.fill()


# ================================================================ PECES
class FishT(Creature):
    float_ = True

    def __init__(self, **p):
        d = dict(color=(1.0, 0.6, 0.2), rx=230, ry=130, stripes=None, teeth=False, puff=False, lure=False,
                 sword=False, long=False, fins=(0.9, 0.5, 0.2), bpm=90)
        d.update(p)
        self.p = d
        self.color = d["color"]

    def _r(self, t):
        p = self.p
        if p["puff"]:
            k = 1 + 0.45 * max(0, math.sin(t * 1.2)) ** 2
            return p["rx"] * (0.8 + 0.3 * k), p["ry"] * k
        return p["rx"], p["ry"]

    def body(self, ctx, t):
        rx, ry = self._r(t)
        ctx.new_path()
        if self.p["long"]:
            self._eel_path(ctx, t)
        else:
            ellipse(ctx, 0, -330, rx, ry)

    def _eel_path(self, ctx, t):
        pts = [(-280 + j * 50, -330 + 40 * math.sin(t * 4 + j * 0.7)) for j in range(13)]
        tube_path(ctx, pts, 104, 50)

    def draw(self, ctx, t):
        p = self.p
        c = p["color"]
        rx, ry = self._r(t)
        if p["long"]:
            pts = [(-280 + j * 50, -330 + 40 * math.sin(t * 4 + j * 0.7)) for j in range(13)]
            tentacle(ctx, pts, 104, 50, c)
            eye(ctx, -290, -350 + 40 * math.sin(t * 4), 18, t, 0.3)
            smile(ctx, -320, -315 + 40 * math.sin(t * 4), 14)
            return
        a = 0.35 * math.sin(t * 7)
        ctx.save()  # cola
        ctx.translate(rx * 0.85, -330)
        ctx.rotate(a)
        _poly(ctx, [(0, 0), (rx * 0.55, -ry * 0.75), (rx * 0.45, 0), (rx * 0.55, ry * 0.75)])
        ctx.restore()
        outline(ctx, p["fins"])
        _poly(ctx, [(-rx * 0.2, -330 - ry * 0.85), (rx * 0.05, -330 - ry * 1.3 - 10 * math.sin(t * 5)), (rx * 0.4, -330 - ry * 0.8)])
        outline(ctx, p["fins"])
        if p["sword"]:
            _poly(ctx, [(-rx * 0.9, -340), (-rx * 2.1, -325), (-rx * 0.9, -310)])
            outline(ctx, shade(c, 0.9), 7)
        if p["lure"]:
            ctx.move_to(-rx * 0.5, -330 - ry * 0.85)
            ctx.curve_to(-rx * 0.6, -330 - ry * 1.8, -rx * 1.3, -330 - ry * 1.7, -rx * 1.35, -330 - ry * 1.1)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(8)
            ctx.stroke()
            gl = 0.6 + 0.4 * math.sin(t * 4)
            ctx.arc(-rx * 1.35, -330 - ry * 1.05, 40 * gl + 20, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.6, 0.35)
            ctx.fill()
            ctx.arc(-rx * 1.35, -330 - ry * 1.05, 18, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 0.7)
            ctx.fill()
        ellipse(ctx, 0, -330, rx, ry)
        outline(ctx, c)
        if p["stripes"]:
            ctx.save()
            ellipse(ctx, 0, -330, rx, ry)
            ctx.clip()
            for x in (-rx * 0.45, rx * 0.15):
                ctx.rectangle(x, -330 - ry, rx * 0.22, ry * 2)
                ctx.set_source_rgb(*p["stripes"])
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(6)
                ctx.stroke()
            ctx.restore()
        if p["puff"]:
            for k in range(18):
                ang = k * 2 * math.pi / 18
                x0, y0 = math.cos(ang) * rx, -330 + math.sin(ang) * ry
                ctx.move_to(x0, y0)
                ctx.line_to(x0 + math.cos(ang) * 30, y0 + math.sin(ang) * 30)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        eye(ctx, -rx * 0.6, -330 - ry * 0.2, ry * 0.24, t, 1.0)
        if p["teeth"]:
            ctx.move_to(-rx * 0.95, -320)
            ctx.line_to(-rx * 0.55, -300)
            ctx.line_to(-rx * 0.95, -280)
            ctx.close_path()
            ctx.set_source_rgb(0.7, 0.15, 0.2)
            ctx.fill()
            for k in range(4):
                x = -rx * 0.93 + k * rx * 0.09
                _poly(ctx, [(x, -318 + k * 4), (x + 12, -300), (x + 24, -316 + k * 4)])
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
        else:
            smile(ctx, -rx * 0.85, -310, ry * 0.12)
        ctx.save()  # aleta lateral
        ctx.translate(-rx * 0.1, -300)
        ctx.rotate(0.4 * math.sin(t * 5))
        _poly(ctx, [(0, 0), (-60, 60), (30, 40)])
        ctx.restore()
        outline(ctx, p["fins"], 7)

    def inside(self, ctx, t):
        rx, ry = self._r(t)
        if self.p["long"]:
            bones(ctx, -280, -330, 320, -330, 9)
            return
        bones(ctx, -rx * 0.7, -330, rx * 0.75, -330, 11)
        for k in range(7):
            x = -rx * 0.45 + k * rx * 0.17
            for sy in (-1, 1):
                ctx.move_to(x, -330)
                ctx.curve_to(x + 8, -330 + sy * ry * 0.4, x + 15, -330 + sy * ry * 0.55, x + 20, -330 + sy * ry * 0.7)
                ctx.set_source_rgb(0.95, 0.97, 1)
                ctx.set_line_width(6)
                ctx.stroke()
        if self.p["puff"]:
            ellipse(ctx, 0, -330, rx * 0.6, ry * 0.6)
            ctx.set_source_rgba(0.7, 0.9, 1, 0.5)
            ctx.fill()
        heart_shape(ctx, -rx * 0.45, -280, ry * 0.18 * (1 + 0.3 * beat(t, self.p["bpm"])), glow=True)


# ================================================================ INSECTOS Y ARAÑAS
class BugT(Creature):
    def __init__(self, **p):
        d = dict(color=(0.25, 0.2, 0.2), legs=6, wings=None, wingc=(0.85, 0.95, 1.0), stripes=None, spots=None,
                 abd=(150, 100), thx=(70, 60), head=55, antenna=True, stinger=False, fly=False, tail=False,
                 pincers=False, y=-230, proboscis=False)
        d.update(p)
        self.p = d
        self.color = d["color"]
        self.float_ = d["fly"]

    def body(self, ctx, t):
        p = self.p
        y = p["y"]
        ctx.new_path()
        ellipse(ctx, 140, y, *p["abd"])
        ctx.new_sub_path()
        ellipse(ctx, -10, y, *p["thx"])
        ctx.new_sub_path()
        ctx.arc(-120, y - 20, p["head"], 0, 2 * math.pi)

    def draw(self, ctx, t):
        p = self.p
        c, y = p["color"], p["y"]
        ax, ay = p["abd"]
        # patas
        n = p["legs"]
        for k in range(n):
            side = k % 2
            i = k // 2
            x0 = -40 + i * (80 / max(1, n // 2 - 1)) if n > 2 else 0
            ph = math.sin(t * 10 + k * 1.3) * 12
            ctx.move_to(x0, y + 20)
            kx = x0 + (-70 + i * 60) + ph
            ctx.line_to(kx, (y + 40) if p["fly"] else (y - 40 if side else y + 30))
            foot = (y + p["thx"][1] + 70) if p["fly"] else -5
            ctx.line_to(kx + (-30 + i * 25), foot)
            ctx.set_source_rgb(*(INK if side else shade(INK, 2)))
            ctx.set_line_width(10)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        # alas traseras
        if p["wings"]:
            flap = math.sin(t * (30 if p["wings"] != "butterfly" else 6))
            ctx.save()
            ctx.translate(0, y - p["thx"][1] * 0.6)
            if p["wings"] == "butterfly":
                for k, (sx, sy) in enumerate(((1, 1.0), (0.8, 0.7))):
                    ctx.save()
                    ctx.scale(1, 0.55 + 0.45 * abs(flap))
                    ellipse(ctx, 120 * sx, -150 * sy, 150 * sx, 130 * sy)
                    ctx.restore()
                    outline(ctx, p["wingc"] if k == 0 else shade(p["wingc"], 0.85))
                    for dx, dy in ((80, -150), (170, -110)):
                        ctx.save()
                        ctx.scale(1, 0.55 + 0.45 * abs(flap))
                        ctx.arc(dx * sx, dy * sy, 28, 0, 2 * math.pi)
                        ctx.restore()
                        outline(ctx, (1, 1, 1), 5)
            else:
                ctx.rotate(-0.3 + 0.25 * flap)
                ellipse(ctx, 80, -90, 110, 50)
                ctx.set_source_rgba(*p["wingc"], 0.65)
                ctx.fill_preserve()
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(6)
                ctx.stroke()
            ctx.restore()
        # cola de escorpión
        if p["tail"]:
            sw = math.sin(t * 3)
            pts = [(140 + ax * 0.8 + j * 25, y - j * 45 - 20 * sw * j / 6 + (j ** 2) * 2) for j in range(7)]
            pts += [(pts[-1][0] - 40, pts[-1][1] - 30)]
            tentacle(ctx, pts, 46, 26, c)
            _poly(ctx, [(pts[-1][0] - 10, pts[-1][1] - 10), (pts[-1][0] - 50, pts[-1][1] + 20), (pts[-1][0] + 5, pts[-1][1] + 25)])
            outline(ctx, (0.95, 0.3, 0.3), 5)
        # abdomen
        ellipse(ctx, 140, y, ax, ay)
        outline(ctx, c)
        ctx.save()
        ellipse(ctx, 140, y, ax, ay)
        ctx.clip()
        if p["stripes"]:
            for k in range(4):
                ctx.rectangle(90 + k * 55, y - ay, 26, ay * 2)
            ctx.set_source_rgb(*p["stripes"])
            ctx.fill()
        if p["spots"]:
            for (a, b) in ((100, -40), (170, 20), (210, -50), (120, 40)):
                ctx.new_sub_path()
                ctx.arc(a, y + b, 22, 0, 2 * math.pi)
            ctx.set_source_rgb(*p["spots"])
            ctx.fill()
        ctx.restore()
        if p["spots"]:  # línea central de mariquita
            ctx.move_to(140 - ax, y)
            ctx.line_to(140 + ax, y)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        if p["stinger"]:
            _poly(ctx, [(140 + ax * 0.95, y - 12), (140 + ax + 50, y), (140 + ax * 0.95, y + 12)])
            outline(ctx, INK, 4)
        # tórax y cabeza
        ellipse(ctx, -10, y, *p["thx"])
        outline(ctx, shade(c, 1.1))
        hr = p["head"]
        hx, hy = -120, y - 20
        if p["pincers"]:
            for sy, ph in ((-1, 0), (1, 1.5)):
                o = 0.3 * math.sin(t * 4 + ph)
                ctx.move_to(hx - hr * 0.6, hy + sy * hr * 0.4)
                ctx.line_to(hx - hr * 2.2, hy + sy * hr * (0.9 + o))
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(26)
                ctx.stroke_preserve()
                ctx.set_source_rgb(*c)
                ctx.set_line_width(14)
                ctx.stroke()
                ctx.arc(hx - hr * 2.4, hy + sy * hr * (1.0 + o), 30, 0, 2 * math.pi)
                outline(ctx, c, 7)
        ctx.arc(hx, hy, hr, 0, 2 * math.pi)
        outline(ctx, c)
        if p["antenna"]:
            for k in (-1, 1):
                w = 0.15 * math.sin(t * 5 + k)
                ctx.move_to(hx - 10, hy - hr * 0.8)
                ctx.curve_to(hx - 40 + 30 * k, hy - hr * 1.8, hx - 80 + 50 * k + 30 * w, hy - hr * 2.2, hx - 100 + 60 * k,
                             hy - hr * 2.4)
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(6)
                ctx.stroke()
                ctx.arc(hx - 100 + 60 * k, hy - hr * 2.4, 9, 0, 2 * math.pi)
                ctx.fill()
        if p["proboscis"]:
            ctx.move_to(hx - hr * 0.8, hy + 10)
            ctx.line_to(hx - hr * 2.6, hy + 60 + 10 * math.sin(t * 8))
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
        eye(ctx, hx - hr * 0.35, hy - hr * 0.1, hr * 0.32, t, 0.5)
        if p["legs"] == 8:  # arañas: varios ojos
            for k in range(3):
                ctx.arc(hx - hr * 0.1 + k * 18, hy - hr * 0.6, 7, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.fill()
        if p["fly"]:
            pass

    def inside(self, ctx, t):
        p = self.p
        y = p["y"]
        flow_line(ctx, [(220, y), (140, y - 20), (-10, y - 10), (-110, y - 20)], t, (0.4, 1.0, 0.5), 9)
        ctx.arc(-120, y - 20, p["head"] * 0.45, 0, 2 * math.pi)
        ctx.set_source_rgba(1.0, 0.7, 0.85, 0.9)
        ctx.fill()
        for k in range(4):
            ellipse(ctx, 90 + k * 40, y + 20, 18, 14 * (1 + 0.15 * math.sin(t * 5 + k)))
            ctx.set_source_rgba(1, 0.85, 0.5, 0.9)
            ctx.fill()


# ================================================================ REPTILES, ANFIBIOS Y MAR
class Snake(Creature):
    color = (0.35, 0.75, 0.35)

    def __init__(self, color=(0.35, 0.75, 0.35), pattern=(0.95, 0.8, 0.2), cobra=False):
        self.color, self.pc, self.cobra = color, pattern, cobra

    def _pts(self, t):
        return [(300 - j * 45, -70 - 40 * math.sin(t * 3 - j * 0.6) - (max(0, j - 9) ** 2) * 18) for j in range(15)]

    def body(self, ctx, t):
        tube_path(ctx, self._pts(t), 30, 56)

    def draw(self, ctx, t):
        pts = self._pts(t)
        tentacle(ctx, pts, 30, 56, self.color)
        for k, (x, y) in enumerate(pts[1:-2]):
            if k % 2 == 0:
                ctx.arc(x, y, 9, 0, 2 * math.pi)
                ctx.set_source_rgb(*self.pc)
                ctx.fill()
        hx, hy = pts[-1]
        if self.cobra:
            ellipse(ctx, hx + 10, hy + 40, 75, 95)
            outline(ctx, shade(self.color, 0.9))
        ellipse(ctx, hx - 20, hy, 65, 45)
        outline(ctx, self.color)
        eye(ctx, hx - 30, hy - 15, 16, t, 0.2)
        if math.sin(t * 5) > 0.3:
            ctx.move_to(hx - 80, hy + 10)
            ctx.line_to(hx - 140, hy + 15)
            ctx.line_to(hx - 160, hy + 0)
            ctx.move_to(hx - 140, hy + 15)
            ctx.line_to(hx - 160, hy + 30)
            ctx.set_source_rgb(0.95, 0.2, 0.3)
            ctx.set_line_width(6)
            ctx.stroke()

    def inside(self, ctx, t):
        pts = self._pts(t)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(8)
        ctx.stroke()
        for x, y in pts[1:-1]:
            ctx.move_to(x, y - 22)
            ctx.line_to(x, y + 22)
        ctx.set_line_width(4)
        ctx.stroke()
        heart_shape(ctx, pts[10][0], pts[10][1], 22 * (1 + 0.25 * beat(t, 50)), glow=True)


class Crocodile(Creature):
    color = (0.35, 0.6, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 60, -140, 260, 80)

    def draw(self, ctx, t):
        c = self.color
        sw = math.sin(t * 2)
        ctx.move_to(280, -150)
        ctx.curve_to(400, -140, 480, -100 + 30 * sw, 560, -60 + 30 * sw)
        ctx.line_to(300, -90)
        outline(ctx, c)
        for x in (-80, 160):
            for dx in (-20, 20):
                _limb(ctx, x + dx, -100, x + dx * 2 + 20 * math.sin(t * 4 + x), -10, 30, shade(c, 0.9))
        ellipse(ctx, 60, -140, 260, 80)
        outline(ctx, c)
        for k in range(8):
            _poly(ctx, [(-120 + k * 50, -210), (-100 + k * 50, -245), (-80 + k * 50, -210)])
            outline(ctx, shade(c, 0.8), 5)
        op = max(0, math.sin(t * 1.5)) ** 2 * 0.45
        ctx.save()  # mandíbulas
        ctx.translate(-180, -150)
        ctx.rotate(op)
        _poly(ctx, [(0, -40), (-280, -20), (-290, 10), (0, 10)])
        outline(ctx, c)
        for k in range(6):
            _poly(ctx, [(-260 + k * 40, 10), (-248 + k * 40, 34), (-236 + k * 40, 10)])
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
        ctx.restore()
        _poly(ctx, [(-180, -130), (-460, -110), (-460, -85), (-180, -80)])
        outline(ctx, shade(c, 1.1))
        eye(ctx, -170, -215, 26, t, 0.8)

    def inside(self, ctx, t):
        bones(ctx, -150, -150, 280, -150, 11)
        for k in range(8):
            ctx.move_to(-100 + k * 45, -150)
            ctx.line_to(-90 + k * 45, -90)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(6)
            ctx.stroke()
        heart_shape(ctx, -40, -130, 32 * (1 + 0.25 * beat(t, 30)), glow=True)
        stomach(ctx, 100, -125, 40, t)


class Turtle(Creature):
    def __init__(self, sea=False):
        self.sea = sea
        self.float_ = sea
        self.color = (0.45, 0.75, 0.45)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -200, 210, math.pi, 2 * math.pi)
        ctx.close_path()

    def draw(self, ctx, t):
        sw = math.sin(t * (3 if self.sea else 2))
        for x in (-150, 150):
            if self.sea:
                ctx.save()
                ctx.translate(x, -190)
                ctx.rotate(0.6 * sw * (1 if x < 0 else -1))
                ellipse(ctx, -60 if x < 0 else 60, 30, 90, 30)
                ctx.restore()
                outline(ctx, self.color)
            else:
                _limb(ctx, x, -170, x + 10 * sw, -10, 50, self.color)
        bob = 10 * math.sin(t * 2)
        ctx.move_to(-190, -230)
        ctx.line_to(-280, -280 + bob)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(70)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(56)
        ctx.stroke()
        ellipse(ctx, -300, -290 + bob, 65, 50)
        outline(ctx, self.color)
        eye(ctx, -320, -305 + bob, 16, t, 0.9)
        smile(ctx, -345, -270 + bob, 14)
        ctx.arc(0, -200, 210, math.pi, 2 * math.pi)
        ctx.close_path()
        outline(ctx, (0.55, 0.4, 0.22))
        for (x, y) in ((-100, -280), (0, -330), (100, -280), (-60, -230), (60, -230)):
            _poly(ctx, [(x - 40, y), (x - 20, y - 35), (x + 20, y - 35), (x + 40, y), (x + 20, y + 35), (x - 20, y + 35)])
            outline(ctx, (0.65, 0.5, 0.3), 5)
        ctx.rectangle(-215, -210, 430, 22)
        outline(ctx, (0.85, 0.8, 0.55), 6)

    def inside(self, ctx, t):
        for k in range(5):
            ctx.arc(0, -200, 60 + k * 30, math.pi * 1.05, math.pi * 1.95)
            ctx.set_source_rgba(0.95, 0.97, 1, 0.7)
            ctx.set_line_width(5)
            ctx.stroke()
        bones(ctx, -170, -230, 170, -210, 10)
        heart_shape(ctx, -40, -260, 28 * (1 + 0.3 * beat(t, 20)), glow=True)
        for sx in (-1, 1):
            ellipse(ctx, sx * 90, -280, 50, 30 * (1 + 0.1 * math.sin(t)))
            ctx.set_source_rgba(1, 0.6, 0.7, 0.8)
            ctx.fill()


class Frog(Creature):
    def __init__(self, color=(0.4, 0.8, 0.35), poison=False):
        self.color, self.poison = color, poison

    def _jump(self, t):
        ph = (t * 0.7) % 1
        return -220 * max(0, math.sin(min(ph / 0.4, 1) * math.pi)) if ph < 0.4 else 0

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -190 + self._jump(t), 180, 140)

    def draw(self, ctx, t):
        c = self.color
        j = self._jump(t)
        ctx.save()
        ctx.translate(0, j)
        stretch = 1 + (0.4 if j < -20 else 0)
        for sx in (-1, 1):
            _limb(ctx, sx * 130, -120, sx * 190, -10 * stretch, 46, shade(c, 0.85))
            ellipse(ctx, sx * 200, -10, 60, 18)
            outline(ctx, shade(c, 0.85), 7)
        ellipse(ctx, 0, -190, 180, 140)
        outline(ctx, c)
        if self.poison:
            for (a, b) in ((-60, -260), (70, -230), (20, -150), (-90, -170)):
                ctx.arc(a, b, 22, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.fill()
        ellipse(ctx, 0, -150, 120, 70)
        ctx.set_source_rgb(*shade(c, 1.3))
        ctx.fill()
        for sx in (-1, 1):
            ctx.arc(sx * 75, -300, 50, 0, 2 * math.pi)
            outline(ctx, c)
            eye(ctx, sx * 75, -305, 34, t, 0.3, look=(0, 0.1))
        if math.sin(t * 2.3) > 0.85:  # lengua
            ctx.move_to(-60, -170)
            ctx.line_to(-380, -260)
            ctx.set_source_rgb(0.95, 0.4, 0.5)
            ctx.set_line_width(16)
            ctx.stroke()
            ctx.arc(-380, -260, 20, 0, 2 * math.pi)
            ctx.fill()
        else:
            ctx.arc(0, -230, 90, 0.35, math.pi - 0.35)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(8)
            ctx.stroke()
        ctx.restore()

    def inside(self, ctx, t):
        j = self._jump(t)
        bones(ctx, 0, -280 + j, 0, -110 + j, 10)
        heart_shape(ctx, -30, -190 + j, 30 * (1 + 0.25 * beat(t, 60)), glow=True)
        for sx in (-1, 1):
            ellipse(ctx, sx * 70, -200 + j, 40, 28 * (1 + 0.15 * math.sin(t * 3)))
            ctx.set_source_rgba(1, 0.6, 0.7, 0.8)
            ctx.fill()


class Lizard(Creature):
    def __init__(self, chameleon=False):
        self.cham = chameleon
        self.color = (0.45, 0.75, 0.4)

    def _c(self, t):
        if not self.cham:
            return self.color
        h = (t * 0.25) % 1
        return tuple(0.5 + 0.45 * math.sin(2 * math.pi * (h + k / 3)) for k in range(3))

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 40, -170, 200, 85)

    def draw(self, ctx, t):
        c = self._c(t)
        sw = math.sin(t * 3)
        if self.cham:
            ctx.arc(330, -170, 70, -math.pi * 0.7, math.pi * 0.9)
        else:
            ctx.move_to(230, -170)
            ctx.curve_to(330, -160, 420, -120 + 40 * sw, 520, -40 + 40 * sw)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(46)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*c)
        ctx.set_line_width(32)
        ctx.stroke()
        for k, x in enumerate((-80, -40, 100, 140)):
            _limb(ctx, x, -130, x + (-50 if k < 2 else 50) + 15 * math.sin(t * 6 + k), -10, 24, shade(c, 0.85))
        ellipse(ctx, 40, -170, 200, 85)
        outline(ctx, c)
        if self.cham:
            for k in range(6):
                _poly(ctx, [(-100 + k * 50, -250), (-80 + k * 50, -275), (-60 + k * 50, -250)])
                outline(ctx, shade(c, 0.8), 4)
        ellipse(ctx, -190, -200, 90, 60)
        outline(ctx, c)
        eye(ctx, -200, -225, 26 if self.cham else 18, t, 0.2,
            look=(math.sin(t * 2) * 0.5, math.cos(t * 1.7) * 0.4) if self.cham else (-0.35, 0.1))
        if self.cham and math.sin(t * 1.9) > 0.8:
            ctx.move_to(-270, -190)
            ctx.line_to(-480, -230)
            ctx.set_source_rgb(0.95, 0.4, 0.5)
            ctx.set_line_width(14)
            ctx.stroke()
            ctx.arc(-480, -230, 22, 0, 2 * math.pi)
            ctx.fill()
        else:
            smile(ctx, -240, -180, 18)

    def inside(self, ctx, t):
        bones(ctx, -170, -190, 230, -170, 9)
        for k in range(7):
            ctx.move_to(-90 + k * 45, -180)
            ctx.line_to(-80 + k * 45, -120)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(5)
            ctx.stroke()
        heart_shape(ctx, -40, -160, 24 * (1 + 0.25 * beat(t, 70)), glow=True)


class Jellyfish(Creature):
    float_ = True

    def __init__(self, color=(1.0, 0.6, 0.85)):
        self.color = color

    def body(self, ctx, t):
        p = 1 + 0.12 * math.sin(t * 3)
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -460)
        ctx.scale(p, 1 / p)
        ctx.arc(0, 0, 170, math.pi, 2 * math.pi)
        ctx.restore()
        ctx.close_path()

    def draw(self, ctx, t):
        for k in range(7):
            x0 = -130 + k * 43
            pts = [(x0 + 25 * math.sin(t * 3 + j * 0.7 + k), -460 + j * 45) for j in range(9)]
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            ctx.set_source_rgba(*self.color, 0.85)
            ctx.set_line_width(10)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        self.body(ctx, t)
        ctx.set_source_rgba(*self.color, 0.85)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(9)
        ctx.stroke()
        eye(ctx, -50, -520, 22, t, 0.5, look=(0, 0.2))
        eye(ctx, 50, -520, 22, t, 0.5, look=(0, 0.2))
        smile(ctx, 0, -480, 20)

    def inside(self, ctx, t):
        for k in range(4):
            ctx.arc(-70 + k * 46, -500, 22, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.6, 0.5 + 0.5 * abs(math.sin(t * 3 + k)))
            ctx.fill()
        flow_line(ctx, [(0, -560), (0, -470), (0, -430)], t, (0.5, 1, 1), 8)


class Crab(Creature):
    color = (0.95, 0.4, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -200, 180, 110)

    def draw(self, ctx, t):
        c = self.color
        side = 40 * math.sin(t * 2)
        ctx.save()
        ctx.translate(side, 0)
        for sx in (-1, 1):
            for k in range(3):
                x0 = sx * (90 + k * 30)
                ph = math.sin(t * 8 + k + sx)
                ctx.move_to(x0, -160)
                ctx.line_to(x0 + sx * 80, -140 + 10 * ph)
                ctx.line_to(x0 + sx * 110, -10)
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(26)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                ctx.stroke_preserve()
                ctx.set_source_rgb(*shade(c, 0.9))
                ctx.set_line_width(14)
                ctx.stroke()
            o = 0.35 * max(0, math.sin(t * 5 + sx))
            ctx.move_to(sx * 140, -230)
            ctx.line_to(sx * 230, -360)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(34)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(20)
            ctx.stroke()
            ctx.save()
            ctx.translate(sx * 250, -400)
            ctx.rotate(-o * sx)
            ellipse(ctx, 0, -20, 55, 40)
            ctx.restore()
            outline(ctx, c)
            ctx.save()
            ctx.translate(sx * 250, -400)
            ctx.rotate(o * sx)
            _poly(ctx, [(-10 * sx, 0), (sx * 60, 25), (sx * 10, 35)])
            ctx.restore()
            outline(ctx, c, 6)
        ellipse(ctx, 0, -200, 180, 110)
        outline(ctx, c)
        for sx in (-1, 1):
            _limb(ctx, sx * 40, -290, sx * 50, -360, 8, INK)
            eye(ctx, sx * 50, -375, 26, t, 0.4, look=(0, 0.1))
        smile(ctx, 0, -190, 30)
        ctx.restore()

    def inside(self, ctx, t):
        ctx.translate(40 * math.sin(t * 2), 0)
        heart_shape(ctx, 0, -230, 30 * (1 + 0.25 * beat(t, 100)), glow=True)
        stomach(ctx, 0, -170, 35, t)
        for sx in (-1, 1):
            ellipse(ctx, sx * 100, -200, 40, 25)
            ctx.set_source_rgba(0.7, 0.9, 1, 0.7)
            ctx.fill()


class Starfish(Creature):
    color = (1.0, 0.6, 0.3)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.save()
        ctx.translate(0, -230)
        ctx.rotate(0.1 * math.sin(t))
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = 220 if k % 2 == 0 else 85
            (ctx.move_to if k == 0 else ctx.line_to)(math.cos(a) * r, math.sin(a) * r)
        ctx.close_path()
        ctx.restore()

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        for k in range(12):
            a = k * 0.52
            ctx.arc(math.cos(a) * 100, -230 + math.sin(a) * 100, 8, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.6)
            ctx.fill()
        eye(ctx, -35, -250, 22, t, 0.5, look=(0, 0))
        eye(ctx, 35, -250, 22, t, 0.5, look=(0, 0))
        smile(ctx, 0, -205, 20)

    def inside(self, ctx, t):
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            flow_line(ctx, [(0, -230), (math.cos(a) * 180, -230 + math.sin(a) * 180)], t, (0.5, 0.9, 1), 7)
        ctx.arc(0, -230, 40, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 0.8, 0.5, 0.9)
        ctx.fill()


class Seahorse(Creature):
    float_ = True
    color = (1.0, 0.75, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, 0, -380, 90, 150)

    def draw(self, ctx, t):
        c = self.color
        ctx.move_to(30, -250)
        ctx.curve_to(80, -150, 40, -60, -20, -60)
        ctx.curve_to(-60, -60, -60, -110, -20, -110)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(56)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*c)
        ctx.set_line_width(42)
        ctx.stroke()
        ellipse(ctx, 0, -380, 90, 150)
        outline(ctx, c)
        for k in range(6):
            ctx.move_to(-70, -460 + k * 40)
            ctx.line_to(70, -450 + k * 40)
        ctx.set_source_rgba(*INK, 0.3)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.save()
        ctx.translate(80, -380)
        ctx.scale(1, 0.5 + 0.5 * abs(math.sin(t * 15)))
        ellipse(ctx, 30, 0, 40, 60)
        ctx.restore()
        outline(ctx, shade(c, 1.1), 6)
        ellipse(ctx, -30, -560, 80, 65)
        outline(ctx, c)
        _poly(ctx, [(-90, -575), (-200, -560), (-200, -530), (-90, -540)])
        outline(ctx, c)
        eye(ctx, -40, -575, 22, t, 0.3)

    def inside(self, ctx, t):
        heart_shape(ctx, -10, -420, 24 * (1 + 0.3 * beat(t, 60)), glow=True)
        ellipse(ctx, 20, -330, 45, 55)  # bolsa con crías (los machos gestan)
        ctx.set_source_rgba(1, 0.85, 0.6, 0.7)
        ctx.fill()
        for k in range(5):
            ctx.arc(5 + (k % 3) * 18, -350 + (k // 3) * 30, 7, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 0.7)
            ctx.fill()


class Dolphin(Creature):
    float_ = True
    color = (0.55, 0.68, 0.82)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-280, -320)
        ctx.curve_to(-200, -450, 150, -440, 230, -330)
        ctx.curve_to(150, -250, -180, -230, -280, -320)
        ctx.close_path()

    def draw(self, ctx, t):
        c = self.color
        a = 0.3 * math.sin(t * 4)
        ctx.save()
        ctx.translate(220, -330)
        ctx.rotate(a - 0.2)
        _poly(ctx, [(0, 0), (110, -80), (70, 0), (110, 80)])
        ctx.restore()
        outline(ctx, shade(c, 0.85))
        _poly(ctx, [(-40, -420), (20, -530), (70, -410)])
        outline(ctx, shade(c, 0.85))
        self.body(ctx, t)
        outline(ctx, c)
        ctx.move_to(-270, -310)
        ctx.curve_to(-170, -250, 100, -260, 200, -320)
        ctx.curve_to(100, -280, -170, -270, -270, -310)
        ctx.set_source_rgb(0.92, 0.95, 1)
        ctx.fill()
        _poly(ctx, [(-280, -330), (-380, -315), (-375, -300), (-270, -305)])
        outline(ctx, c)
        eye(ctx, -200, -350, 20, t, 0.6)
        smile(ctx, -300, -305, 22)

    def inside(self, ctx, t):
        bones(ctx, -220, -340, 200, -335, 10)
        heart_shape(ctx, -100, -320, 34 * (1 + 0.2 * beat(t, 100)), glow=True)
        ellipse(ctx, -240, -360, 30, 22)  # melón (ecolocalización)
        ctx.set_source_rgba(1, 1, 0.7, 0.8)
        ctx.fill()
        for k in range(3):
            ph = (t * 1.2 + k / 3) % 1
            ctx.arc(-260, -350, 30 + ph * 180, math.pi * 0.8, math.pi * 1.2)
            ctx.set_source_rgba(1, 1, 0.6, 1 - ph)
            ctx.set_line_width(6)
            ctx.stroke()


class Monkey(Creature):
    def __init__(self, color=(0.6, 0.42, 0.28), gorilla=False):
        self.color, self.gorilla = color, gorilla

    def body(self, ctx, t):
        s = 1.3 if self.gorilla else 1.0
        ctx.new_path()
        ellipse(ctx, 0, -260 * s, 120 * s, 140 * s)
        ctx.new_sub_path()
        ctx.arc(0, -470 * s, 95 * s, 0, 2 * math.pi)

    def draw(self, ctx, t):
        s = 1.3 if self.gorilla else 1.0
        c = self.color
        face = (0.95, 0.8, 0.65) if not self.gorilla else (0.45, 0.42, 0.45)
        sw = math.sin(t * 5)
        if not self.gorilla:
            ctx.move_to(100, -200)
            ctx.curve_to(260, -200, 260, -420 + 40 * sw, 180, -460)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(36)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*c)
            ctx.set_line_width(22)
            ctx.stroke()
        for sx in (-1, 1):
            _limb(ctx, sx * 60 * s, -160 * s, sx * 80 * s, -5, 40 * s, shade(c, 0.9))
            up = (sw if sx < 0 else -sw)
            _limb(ctx, sx * 100 * s, -330 * s, sx * (170 + 30 * up) * s, (-150 - 160 * max(0, up)) * s, 36 * s, c)
        ellipse(ctx, 0, -260 * s, 120 * s, 140 * s)
        outline(ctx, c)
        ellipse(ctx, 0, -240 * s, 70 * s, 90 * s)
        ctx.set_source_rgb(*face)
        ctx.fill()
        for sx in (-1, 1):
            ctx.arc(sx * 95 * s, -480 * s, 32 * s, 0, 2 * math.pi)
            outline(ctx, face)
        ctx.arc(0, -470 * s, 95 * s, 0, 2 * math.pi)
        outline(ctx, c)
        ellipse(ctx, 0, -450 * s, 70 * s, 65 * s)
        ctx.set_source_rgb(*face)
        ctx.fill()
        eye(ctx, -28 * s, -485 * s, 18 * s, t, 0.4, look=(-0.3, 0))
        eye(ctx, 28 * s, -485 * s, 18 * s, t, 0.4, look=(-0.3, 0))
        smile(ctx, 0, -425 * s, 28 * s, max(0, math.sin(t * 3)) * 0.5)

    def inside(self, ctx, t):
        s = 1.3 if self.gorilla else 1.0
        ctx.arc(0, -470 * s, 70 * s, 0, 2 * math.pi)
        ctx.set_source_rgb(0.95, 0.97, 1)
        ctx.set_line_width(8)
        ctx.stroke()
        ellipse(ctx, 0, -490 * s, 50 * s, 35 * s)
        ctx.set_source_rgba(1, 0.68, 0.8, 0.9)
        ctx.fill()
        bones(ctx, 0, -380 * s, 0, -150 * s, 11)
        heart_shape(ctx, -25 * s, -290 * s, 30 * s * (1 + 0.25 * beat(t, 90)), glow=True)
        stomach(ctx, 20 * s, -210 * s, 30 * s, t)


class Squid(Creature):
    float_ = True
    color = (1.0, 0.55, 0.5)

    def body(self, ctx, t):
        ctx.new_path()
        _poly(ctx, [(0, -720), (110, -520), (90, -330), (-90, -330), (-110, -520)])

    def draw(self, ctx, t):
        c = self.color
        for k in range(8):
            x0 = -70 + k * 20
            L = 280 if k in (2, 5) else 200
            pts = [(x0 + 30 * math.sin(t * 3 + j * 0.6 + k) * j / 8 + (k - 3.5) * 8 * j / 8, -330 + j * L / 8) for j in range(9)]
            tentacle(ctx, pts, 26, 10, shade(c, 0.95))
        for sx in (-1, 1):
            _poly(ctx, [(sx * 60, -700), (sx * 170, -620 + 10 * math.sin(t * 4)), (sx * 90, -560)])
            outline(ctx, shade(c, 0.9))
        self.body(ctx, t)
        outline(ctx, c)
        eye(ctx, -45, -400, 30, t, 0.7, look=(0, 0.1))
        eye(ctx, 45, -400, 30, t, 0.7, look=(0, 0.1))

    def inside(self, ctx, t):
        for x in (-35, 35):
            heart_shape(ctx, x, -470, 20 * (1 + 0.3 * beat(t + x, 80)), glow=True)
        heart_shape(ctx, 0, -530, 26 * (1 + 0.3 * beat(t, 80)), glow=True)
        ellipse(ctx, 0, -620, 30, 60)
        ctx.set_source_rgba(0.2, 0.2, 0.3, 0.9)  # bolsa de tinta
        ctx.fill()


# ================================================================ CATÁLOGO
Q = Quadruped
ANIMALS = {
    "dog": Q(color=(0.85, 0.65, 0.4), ears="floppy", snout="dog", tail="thin", pattern="patches", pcolor=(0.55, 0.38, 0.22)),
    "wolf": Q(color=(0.6, 0.62, 0.68), belly=(0.88, 0.88, 0.9), ears="pointy", snout="dog", tail="bushy"),
    "fox": Q(color=(0.95, 0.5, 0.2), belly=(1, 0.95, 0.9), ears="pointy", snout="dog", tail="bushy", brx=170, bry=90, legw=26),
    "lion": Q(color=(0.95, 0.75, 0.4), ears="small", snout="cat", tail="tuft", extras=("mane",), nose=(0.5, 0.3, 0.25)),
    "tiger": Q(color=(1.0, 0.6, 0.2), belly=(1, 0.95, 0.9), ears="small", snout="cat", tail="long", pattern="stripes"),
    "cheetah": Q(color=(0.98, 0.8, 0.45), ears="small", snout="cat", tail="long", pattern="spots", brx=200, bry=85, legw=24, leg=200),
    "elephant": Q(color=(0.65, 0.67, 0.72), bx=60, by=-330, brx=230, bry=150, legw=60, head=(-170, -440, 110), ears="big",
                  snout="trunk", tail="tuft", extras=("tusks",), walk=True, bpm=30),
    "giraffe": Q(color=(1.0, 0.82, 0.4), bx=80, by=-360, brx=170, bry=95, legw=28, head=(-170, -850, 65), neck=(-165, -820),
                 ears="small", snout="long", tail="tuft", pattern="giraffe", pcolor=(0.7, 0.42, 0.2), extras=("ossicones",)),
    "horse": Q(color=(0.62, 0.4, 0.25), ears="pointy", snout="long", tail="long", extras=("hooves", "mane_none"),
               head=(-210, -470, 75), neck=(-195, -450), bry=100, legw=30),
    "zebra": Q(color=(0.97, 0.97, 0.97), ears="pointy", snout="long", tail="tuft", pattern="stripes", pcolor=INK,
               head=(-210, -470, 75), neck=(-195, -450), bry=100, legw=30, extras=("hooves",)),
    "cow": Q(color=(0.97, 0.97, 0.97), ears="floppy", snout="cow", tail="tuft", pattern="patches", pcolor=INK,
             extras=("horns", "hooves"), nose=(0.95, 0.6, 0.65)),
    "pig": Q(color=(1.0, 0.72, 0.75), ears="pointy", snout="pig", tail="curly", brx=180, bry=120, leg=110),
    "sheep": Q(color=(0.97, 0.97, 0.95), ears="floppy", snout="cow", tail="short", pattern="spots", pcolor=(0.88, 0.88, 0.85), leg=120),
    "bear": Q(color=(0.5, 0.33, 0.2), ears="round", snout="bear", tail="short", brx=210, bry=130, legw=52, leg=130, head=(-180, -410, 95)),
    "polar_bear": Q(color=(0.97, 0.97, 1.0), ears="round", snout="bear", tail="short", brx=210, bry=130, legw=52, leg=130,
                    head=(-180, -410, 95)),
    "panda": Q(color=(0.97, 0.97, 0.97), ears="round", snout="bear", tail="short", brx=200, bry=130, legw=52, leg=120,
               head=(-180, -410, 95), pattern="panda"),
    "rhino": Q(color=(0.62, 0.6, 0.6), ears="pointy", snout="hippo", tail="tuft", brx=230, bry=140, legw=56, leg=130,
               head=(-200, -380, 90), extras=("horn",), bpm=40),
    "hippo": Q(color=(0.62, 0.55, 0.65), ears="small", snout="hippo", tail="short", brx=240, bry=150, legw=60, leg=100,
               head=(-200, -360, 100), bpm=40),
    "camel": Q(color=(0.85, 0.68, 0.45), ears="small", snout="long", tail="tuft", extras=("hump",), leg=230,
               head=(-220, -620, 65), neck=(-200, -590), bry=90, legw=28),
    "deer": Q(color=(0.75, 0.5, 0.3), ears="pointy", snout="long", tail="short", extras=("antlers", "hooves"), leg=210,
              legw=22, bry=85, head=(-190, -480, 65), neck=(-180, -460), pattern="spots", pcolor=(1, 1, 1)),
    "rabbit": Q(color=(0.85, 0.82, 0.8), ears="long", snout="cat", tail="short", brx=150, bry=110, leg=70, legw=40,
                head=(-130, -330, 75), walk=False, nose=(1, 0.5, 0.6), bpm=200),
    "mouse": Q(color=(0.7, 0.7, 0.75), ears="round", snout="mouse", tail="long", brx=150, bry=95, leg=60, legw=22,
               head=(-140, -230, 70), by=-200, nose=(1, 0.5, 0.6), bpm=400),
    "cat2": Q(color=(0.4, 0.4, 0.45), ears="pointy", snout="cat", tail="long", brx=160, bry=90, legw=26, nose=(1, 0.5, 0.6)),
    "kangaroo_none": None,
    # aves
    "penguin": BirdT(color=(0.15, 0.15, 0.2), belly=(1, 1, 1), fly=False, beak="short", legs="short", tail="none",
                     size=1.2, extras=("mask",), y=-200),
    "owl": BirdT(color=(0.6, 0.45, 0.3), belly=(0.9, 0.82, 0.65), fly=False, bigeyes=True, beak="hook", extras=("ears",),
                 beakc=(0.95, 0.75, 0.3), y=-260),
    "eagle": BirdT(color=(0.45, 0.3, 0.2), belly=(1, 1, 1), beak="hook", size=1.2, y=-420),
    "parrot": BirdT(color=(0.2, 0.75, 0.35), belly=(1.0, 0.85, 0.2), beak="hook", crest=True, tail="long",
                    beakc=(0.95, 0.95, 0.9), y=-400),
    "chicken": BirdT(color=(1, 1, 1), belly=(1, 1, 1), fly=False, beak="short", extras=("comb",), y=-220),
    "duck": BirdT(color=(0.95, 0.85, 0.3), belly=(1, 0.95, 0.6), fly=False, beak="flat", y=-200, legs="short"),
    "flamingo": BirdT(color=(1.0, 0.55, 0.65), belly=(1.0, 0.7, 0.75), fly=False, beak="bent", legs="long",
                      neck=340, y=-470, beakc=(0.25, 0.2, 0.2), legc=(1.0, 0.5, 0.6)),
    "toucan": BirdT(color=(0.15, 0.15, 0.2), belly=(1, 0.95, 0.9), beak="big", beakc=(1.0, 0.6, 0.15), y=-400),
    "ostrich": BirdT(color=(0.3, 0.25, 0.25), belly=(0.4, 0.35, 0.35), fly=False, beak="short", legs="long", neck=320,
                     size=1.2, y=-480, legc=(0.95, 0.75, 0.65)),
    "hummingbird": BirdT(color=(0.2, 0.75, 0.65), belly=(0.6, 0.95, 0.85), beak="long", size=0.7, y=-450,
                         beakc=(0.2, 0.2, 0.2), legs="none", bpm=600),
    "crow": BirdT(color=(0.18, 0.18, 0.22), belly=(0.25, 0.25, 0.3), beak="short", beakc=(0.3, 0.3, 0.32), y=-420),
    "bat_none": None,
    # peces
    "clownfish": FishT(color=(1.0, 0.55, 0.15), stripes=(1, 1, 1), fins=(1.0, 0.45, 0.1)),
    "piranha": FishT(color=(0.55, 0.6, 0.65), teeth=True, fins=(0.9, 0.3, 0.3)),
    "pufferfish": FishT(color=(0.95, 0.85, 0.45), puff=True, rx=170, ry=140, fins=(0.9, 0.75, 0.35)),
    "anglerfish": FishT(color=(0.35, 0.3, 0.4), teeth=True, lure=True, fins=(0.3, 0.25, 0.35)),
    "swordfish": FishT(color=(0.4, 0.5, 0.75), sword=True, rx=250, ry=100, fins=(0.3, 0.4, 0.65)),
    "eel": FishT(color=(0.45, 0.55, 0.35), long=True),
    "goldfish": FishT(color=(1.0, 0.65, 0.1), rx=180, ry=120, fins=(1.0, 0.8, 0.3)),
    # insectos
    "ant": BugT(color=(0.3, 0.2, 0.18), abd=(110, 85), thx=(55, 45), head=60, y=-110),
    "bee": BugT(color=(1.0, 0.8, 0.15), stripes=INK, wings="clear", stinger=True, fly=True, y=-380, legs=6),
    "butterfly": BugT(color=(0.25, 0.2, 0.25), wings="butterfly", wingc=(0.6, 0.45, 0.95), abd=(120, 40), thx=(45, 40),
                      head=40, fly=True, y=-420),
    "ladybug": BugT(color=(0.92, 0.2, 0.2), spots=INK, abd=(140, 115), thx=(40, 40), head=50, y=-150),
    "spider": BugT(color=(0.25, 0.22, 0.25), legs=8, antenna=False, abd=(140, 120), thx=(70, 60), head=45, y=-200),
    "mosquito": BugT(color=(0.4, 0.35, 0.3), wings="clear", abd=(130, 35), thx=(45, 40), head=35, fly=True,
                     proboscis=True, y=-420),
    "fly": BugT(color=(0.25, 0.3, 0.3), wings="clear", abd=(100, 70), thx=(60, 55), head=55, fly=True, y=-400,
                wingc=(0.8, 0.9, 1.0)),
    "beetle": BugT(color=(0.2, 0.45, 0.35), abd=(150, 110), thx=(60, 55), head=50, pincers=True, y=-160),
    "cockroach": BugT(color=(0.5, 0.3, 0.18), abd=(160, 80), thx=(70, 50), head=45, y=-120),
    "scorpion": BugT(color=(0.35, 0.28, 0.2), legs=8, antenna=False, tail=True, pincers=True, abd=(120, 70), thx=(60, 50),
                     head=45, y=-120),
    # reptiles, anfibios y mar
    "snake": Snake(),
    "cobra": Snake(color=(0.55, 0.45, 0.3), pattern=(0.85, 0.75, 0.55), cobra=True),
    "crocodile": Crocodile(),
    "turtle": Turtle(),
    "sea_turtle": Turtle(sea=True),
    "frog": Frog(),
    "poison_frog": Frog(color=(0.2, 0.55, 1.0), poison=True),
    "lizard": Lizard(),
    "chameleon": Lizard(chameleon=True),
    "jellyfish": Jellyfish(),
    "crab": Crab(),
    "starfish": Starfish(),
    "seahorse": Seahorse(),
    "dolphin": Dolphin(),
    "squid": Squid(),
    "monkey": Monkey(),
    "gorilla": Monkey(color=(0.25, 0.24, 0.27), gorilla=True),
}
ANIMALS = {k: v for k, v in ANIMALS.items() if v is not None}
for _k in ("cat2",):
    ANIMALS.pop(_k, None)

# partes para la lupa del zoom (aproximadas a partir de la geometría)
def _parts(name, a):
    if isinstance(a, Quadruped):
        p = a.p
        bx, by, brx, bry = p["bx"], p["by"], p["brx"], p["bry"]
        hx, hy, hr = p["head"]
        return {"heart": (bx - brx * 0.35, by), "brain": (hx + hr * 0.1, hy - hr * 0.15), "stomach": (bx + brx * 0.2, by + bry * 0.2),
                "body": (bx, by), "eye": (hx - hr * 0.35, hy - hr * 0.25), "lungs": (bx - brx * 0.3, by - bry * 0.3)}
    if isinstance(a, BirdT):
        bx, by, rx, ry = a._geo()
        return {"heart": (bx - rx * 0.3, by + ry * 0.1), "body": (bx, by), "lungs": (bx + rx * 0.2, by + ry * 0.35),
                "wing": (bx + rx * 0.6, by - ry * 0.5)}
    if isinstance(a, FishT):
        return {"heart": (-a.p["rx"] * 0.45, -280), "body": (0, -330), "gills": (-a.p["rx"] * 0.5, -320)}
    if isinstance(a, BugT):
        y = a.p["y"]
        return {"body": (140, y), "head": (-120, y - 20), "brain": (-120, y - 20), "stomach": (140, y + 20)}
    return {"body": (0, -300)}


ANIMAL_PARTS = {k: _parts(k, v) for k, v in ANIMALS.items()}
