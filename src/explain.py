"""Explicaciones visuales concretas: lupa con zoom que muestra un PROCESO y gráficas animadas.

zoom = {"of": "brain", "title": "DENTRO DEL CEREBRO",
        "items": [{"kind": "cells", "label": "NEURONAS", "do": "shrink"},
                  {"kind": "fluid", "label": "LÍQUIDO", "do": "flow"},
                  {"kind": "particles", "label": "RESIDUOS", "do": "exit"}]}
chart = {"type": "bars", "title": "...", "items": [{"label": "Humano", "value": 1.4}, ...], "unit": "kg"}
chart = {"type": "counter", "to": 100000, "prefix": "", "suffix": " km", "title": "..."}
"""
import math
import random

import cairo

INK = (0.11, 0.11, 0.13)

KINDS = ["cells", "fluid", "particles", "blood", "virus", "atoms", "dna", "waves", "bubbles", "heat"]
DOS = {
    "cells": ["shrink", "grow", "pulse", "divide", "still"],
    "fluid": ["flow"],
    "particles": ["exit", "enter", "wiggle", "gather"],
    "blood": ["flow", "fast", "slow", "blocked"],
    "virus": ["attack", "die", "wiggle"],
    "atoms": ["spin", "split"],
    "dna": ["spin"],
    "waves": ["flow"],
    "bubbles": ["rise"],
    "heat": ["rise"],
}
COLORS = {
    "rosa": (1.0, 0.66, 0.78), "azul": (0.35, 0.65, 1.0), "verde": (0.35, 0.8, 0.45),
    "amarillo": (1.0, 0.85, 0.2), "rojo": (0.92, 0.25, 0.28), "morado": (0.65, 0.45, 0.95),
    "naranja": (1.0, 0.6, 0.2), "gris": (0.55, 0.55, 0.6), "blanco": (0.97, 0.97, 0.97),
    "marron": (0.6, 0.42, 0.28),
}
DEFAULT_COLOR = {"cells": "rosa", "fluid": "azul", "particles": "verde", "blood": "rojo", "virus": "verde",
                 "atoms": "amarillo", "dna": "morado", "waves": "azul", "bubbles": "blanco", "heat": "naranja"}


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def pop(x, k=1.9):
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def _col(item):
    return COLORS.get(item.get("color"), COLORS[DEFAULT_COLOR.get(item.get("kind"), "azul")])


def _outline(ctx, fill, lw=6):
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(lw)
    ctx.stroke()


def _font(ctx, size, bold=True):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def _text(ctx, txt, x, y, size, fill=(1, 1, 1), stroke=INK, lw=10, max_w=None, anchor="c"):
    _font(ctx, size)
    e = ctx.text_extents(txt)
    if max_w and e.width > max_w:
        _font(ctx, size * max_w / e.width)
        e = ctx.text_extents(txt)
    dx = {"c": -e.width / 2, "l": 0, "r": -e.width}[anchor] - e.x_bearing
    ctx.move_to(x + dx, y - e.height / 2 - e.y_bearing)
    ctx.text_path(txt)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if stroke:
        ctx.set_source_rgb(*stroke)
        ctx.set_line_width(lw)
        ctx.stroke_preserve()
    ctx.set_source_rgb(*fill)
    ctx.fill()


# ---------------------------------------------------------------- elementos del micro-mundo
class Micro:
    """Dibuja los elementos dentro del círculo de radio R (origen en el centro)."""

    def __init__(self, items, R, seed=1):
        self.items = items
        self.R = R
        self.rnd = random.Random(seed)
        kinds = {i.get("kind") for i in items}
        self.has_cells = "cells" in kinds
        r = R * 0.17
        self.cells = []
        if self.has_cells:
            sp = r * 2.35
            for gy in range(-4, 5):
                for gx in range(-4, 5):
                    x = gx * sp + (gy % 2) * sp / 2 + self.rnd.uniform(-8, 8)
                    y = gy * sp * 0.88 + self.rnd.uniform(-8, 8)
                    if math.hypot(x, y) < R + r:
                        self.cells.append((x, y, r * self.rnd.uniform(0.9, 1.1), self.rnd.uniform(0, 6)))
        self.points = [(self.rnd.uniform(-R, R), self.rnd.uniform(-R, R), self.rnd.uniform(0, 6)) for _ in range(18)]

    def cell_scale(self, do, t):
        if do == "shrink":
            return 1 - 0.38 * ease((t - 0.7) / 1.6)
        if do == "grow":
            return 0.75 + 0.3 * ease((t - 0.7) / 1.6)
        if do == "pulse":
            return 1 + 0.08 * math.sin(t * 5)
        return 1.0

    def draw(self, ctx, t):
        order = ["fluid", "waves", "heat", "blood", "cells", "dna", "atoms", "bubbles", "particles", "virus"]
        for kind in order:
            for it in self.items:
                if it.get("kind") == kind:
                    getattr(self, "_" + kind)(ctx, it, t)

    def anchor(self, item, t, toward=(0.0, 0.0)):
        """Punto del elemento cercano a su etiqueta, para que la flecha sea corta."""
        k, R = item.get("kind"), self.R
        tx, ty = toward[0] * R * 0.5, toward[1] * R * 0.5
        if k == "cells" and self.cells:
            x, y, _, _ = min(self.cells, key=lambda c: math.hypot(c[0] - tx, c[1] - ty))
            return x, y
        if k == "particles":
            best = min(self.points, key=lambda p: math.hypot(p[0] - tx, p[1] - ty))
            return best[0], best[1]
        return tx, ty

    # --- tipos
    def _fluid(self, ctx, it, t):
        R, c = self.R, _col(it)
        ctx.rectangle(-R, -R, 2 * R, 2 * R)
        ctx.set_source_rgba(*c, 0.55)
        ctx.fill()
        ctx.set_line_width(6)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(9):
            y0 = -R + k * R / 4.2
            ctx.set_source_rgba(1, 1, 1, 0.55)
            for j in range(4):
                x = ((t * 160 + j * R * 0.6 + k * 70) % (2.6 * R)) - 1.3 * R
                ctx.move_to(x, y0 + 8 * math.sin(x / 40 + k))
                ctx.line_to(x + 50, y0 + 8 * math.sin((x + 50) / 40 + k))
            ctx.stroke()

    def _cells(self, ctx, it, t):
        c, do = _col(it), it.get("do", "still")
        s = self.cell_scale(do, t)
        for (x, y, r, ph) in self.cells:
            rr = r * s * (1 + 0.03 * math.sin(t * 3 + ph))
            if do == "divide" and t > 1.0 and int(ph * 10) % 3 == 0:
                d = rr * 0.6 * ease((t - 1.0) / 1.2)
                for sx in (-1, 1):
                    ctx.arc(x + sx * d, y, rr * 0.75, 0, 2 * math.pi)
                    _outline(ctx, c)
                continue
            ctx.save()
            ctx.translate(x, y)
            ctx.scale(1, 0.92 + 0.08 * math.sin(t * 2 + ph))
            ctx.arc(0, 0, rr, 0, 2 * math.pi)
            ctx.restore()
            _outline(ctx, c)
            # prolongaciones (dendritas) y núcleo
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(4)
            for a in range(3):
                ang = ph + a * 2.1
                ctx.move_to(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
                ctx.line_to(x + math.cos(ang) * rr * 1.35, y + math.sin(ang) * rr * 1.35)
            ctx.stroke()
            ctx.arc(x, y, rr * 0.32, 0, 2 * math.pi)
            ctx.set_source_rgb(*[v * 0.75 for v in c])
            ctx.fill()

    def _particles(self, ctx, it, t, virus=False):
        c, do, R = _col(it), it.get("do", "wiggle"), self.R
        for k, (x0, y0, ph) in enumerate(self.points):
            x, y, a = x0, y0, 1.0
            if do == "exit":
                start = 0.8 + (k % 6) * 0.12
                x = x0 + max(0.0, t - start) * 230
                a = 1 - ease((x - R * 0.85) / (R * 0.4))
            elif do == "enter":
                k2 = ease((t - 0.5 - (k % 6) * 0.1) / 1.2)
                x = -1.5 * R + (x0 + 1.5 * R) * k2
            elif do == "gather":
                k2 = ease((t - 0.6) / 1.5)
                x, y = x0 * (1 - 0.7 * k2), y0 * (1 - 0.7 * k2)
            x += 6 * math.sin(t * 7 + ph)
            y += 6 * math.cos(t * 6 + ph)
            if a <= 0.02:
                continue
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(t * 2 + ph)
            ctx.push_group()
            for j in range(5):
                ang = j * 2 * math.pi / 5
                rr = 15 if j % 2 else 12
                ctx.line_to(math.cos(ang) * rr, math.sin(ang) * rr)
            ctx.close_path()
            _outline(ctx, c, 4)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(a)
            ctx.restore()

    def _virus(self, ctx, it, t):
        c, do, R = _col(it), it.get("do", "wiggle"), self.R
        for k in range(4):
            ang0 = k * math.pi / 2 + 0.6
            d = R * 0.62
            if do == "attack":
                d = R * (0.75 - 0.4 * ease((t - 0.6) / 1.6))
            x, y = math.cos(ang0) * d, math.sin(ang0) * d
            s = 1.0
            if do == "die":
                s = 1 - ease((t - 1.0 - k * 0.2) / 0.6)
            if s <= 0.02:
                continue
            ctx.save()
            ctx.translate(x + 5 * math.sin(t * 8 + k), y)
            ctx.rotate(t * 1.5 + k)
            ctx.scale(s, s)
            r = R * 0.13
            for j in range(10):
                a = j * math.pi / 5
                ctx.move_to(math.cos(a) * r, math.sin(a) * r)
                ctx.line_to(math.cos(a) * r * 1.55, math.sin(a) * r * 1.55)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
            for j in range(10):
                a = j * math.pi / 5
                ctx.arc(math.cos(a) * r * 1.6, math.sin(a) * r * 1.6, 7, 0, 2 * math.pi)
                ctx.fill()
            ctx.arc(0, 0, r, 0, 2 * math.pi)
            _outline(ctx, c)
            for sx in (-1, 1):
                ctx.arc(sx * r * 0.35, -r * 0.15, r * 0.14, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.fill()
            ctx.restore()

    def _blood(self, ctx, it, t):
        c, do, R = _col(it), it.get("do", "flow"), self.R
        speed = {"fast": 420, "slow": 90, "blocked": 0}.get(do, 220)
        for vy in (-R * 0.35, R * 0.35):
            h = R * 0.38
            ctx.rectangle(-R * 1.2, vy - h / 2, R * 2.4, h)
            _outline(ctx, (1.0, 0.85, 0.85), 8)
            ctx.save()
            ctx.rectangle(-R * 1.2, vy - h / 2, R * 2.4, h)
            ctx.clip()
            for k in range(14):
                x = ((k * R * 0.22 + t * speed) % (R * 3)) - R * 1.5
                if do == "blocked":
                    x = min(x, R * 0.3 - (13 - k) * 30)
                ctx.save()
                ctx.translate(x, vy + 18 * math.sin(k * 1.7))
                ctx.rotate(k + t)
                ctx.scale(1, 0.55)
                ctx.arc(0, 0, h * 0.28, 0, 2 * math.pi)
                ctx.restore()
                _outline(ctx, c, 4)
            ctx.restore()

    def _atoms(self, ctx, it, t):
        c, do, R = _col(it), it.get("do", "spin"), self.R
        sp = ease((t - 1.0) / 0.8) if do == "split" else 0
        for side in ((-1, 1) if sp > 0 else (0,)):
            cx = side * R * 0.45 * sp
            for j in range(7):
                a = j * 0.9
                ctx.arc(cx + math.cos(a) * 20, math.sin(a) * 20, 18, 0, 2 * math.pi)
                _outline(ctx, (0.95, 0.35, 0.3) if j % 2 else (0.55, 0.6, 0.9), 4)
        if sp > 0 and sp < 1:
            ctx.arc(0, 0, R * 0.9 * sp, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 0.7, 0.8 * (1 - sp))
            ctx.fill()
        if sp == 0:
            for k in range(3):
                ctx.save()
                ctx.rotate(k * math.pi / 3)
                ctx.scale(1, 0.35)
                ctx.arc(0, 0, R * 0.75, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(4)
                ctx.stroke()
                a = t * (2 + k) + k
                ex, ey = math.cos(a) * R * 0.75, math.sin(a) * R * 0.75 * 0.35
                ca, sa = math.cos(k * math.pi / 3), math.sin(k * math.pi / 3)
                ctx.arc(ex * ca - ey * sa, ex * sa + ey * ca, 14, 0, 2 * math.pi)
                _outline(ctx, c, 4)

    def _dna(self, ctx, it, t):
        c, R = _col(it), self.R
        for k in range(26):
            y = -R + k * R / 12.5
            ph = y / 45 + t * 2.5
            x1, x2 = math.sin(ph) * R * 0.38, -math.sin(ph) * R * 0.38
            ctx.move_to(x1, y)
            ctx.line_to(x2, y)
            ctx.set_source_rgb(*([1, 0.8, 0.3] if k % 2 else [0.4, 0.8, 1]))
            ctx.set_line_width(8)
            ctx.stroke()
            for x, z in ((x1, math.cos(ph)), (x2, -math.cos(ph))):
                ctx.arc(x, y, 11 + 4 * z, 0, 2 * math.pi)
                _outline(ctx, c, 3)

    def _waves(self, ctx, it, t):
        c, R = _col(it), self.R
        for k in range(3):
            ctx.move_to(-R, 0)
            for j in range(41):
                x = -R + j * R / 20
                ctx.line_to(x, (k - 1) * R * 0.45 + 30 * math.sin(x / 35 - t * 5 + k))
            ctx.set_source_rgb(*c)
            ctx.set_line_width(12)
            ctx.stroke()

    def _bubbles(self, ctx, it, t):
        c, R = _col(it), self.R
        for k, (x0, y0, ph) in enumerate(self.points):
            y = R - ((t * 120 + (y0 + R)) % (2.2 * R))
            ctx.arc(x0 + 10 * math.sin(t * 3 + ph), y, 10 + (k % 4) * 6, 0, 2 * math.pi)
            ctx.set_source_rgba(*c, 0.6)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(3)
            ctx.stroke()

    def _heat(self, ctx, it, t):
        c, R = _col(it), self.R
        for k in range(6):
            x0 = -R * 0.8 + k * R * 0.32
            ctx.move_to(x0, R)
            for j in range(20):
                y = R - j * R / 9
                ctx.line_to(x0 + 14 * math.sin(y / 25 + t * 6 + k), y - (t * 60) % 40)
            ctx.set_source_rgba(*c, 0.8)
            ctx.set_line_width(8)
            ctx.stroke()


# ---------------------------------------------------------------- lupa
def _pill(ctx, txt, x, y, color):
    _font(ctx, 40)
    e = ctx.text_extents(txt)
    w, h = e.width + 70, 64
    x0 = min(max(x - w / 2, 18), 1080 - w - 18)
    ctx.new_path()
    r = h / 2
    ctx.arc(x0 + r, y, r, math.pi / 2, 3 * math.pi / 2)
    ctx.arc(x0 + w - r, y, r, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    _outline(ctx, (1, 1, 1), 6)
    ctx.arc(x0 + 30, y, 12, 0, 2 * math.pi)
    _outline(ctx, color, 3)
    ctx.move_to(x0 + 50 - e.x_bearing, y - e.height / 2 - e.y_bearing)
    ctx.set_source_rgb(*INK)
    ctx.show_text(txt)
    return x0 + w / 2


LABEL_SPOTS = [(-0.95, -1.08), (0.95, -1.08), (-1.0, 1.1), (1.0, 1.1)]


def draw_zoom(ctx, spec, t, center, R, anchor=None, xray=False, seed=1, cont=False):
    items = [i for i in (spec.get("items") or []) if i.get("kind") in KINDS][:4]
    if not items:
        return
    k = 1.0 if cont else pop((t - 0.2) / 0.4)
    if k <= 0:
        return
    cx, cy = center
    # cono de la lupa desde la parte del cuerpo
    if anchor is not None:
        ax, ay = anchor
        dx, dy = cx - ax, cy - ay
        d = math.hypot(dx, dy) or 1
        px, py = -dy / d * R * k, dx / d * R * k
        ctx.move_to(ax, ay)
        ctx.line_to(cx + px, cy + py)
        ctx.line_to(cx - px, cy - py)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.38)
        ctx.fill()
        ctx.arc(ax, ay, 26 + 6 * math.sin(t * 6), 0, 2 * math.pi)
        ctx.set_source_rgba(0.45, 0.95, 1.0, 0.9)
        ctx.set_line_width(8)
        ctx.stroke()

    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    ctx.arc(0, 0, R + 16, 0, 2 * math.pi)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.save()
    ctx.arc(0, 0, R, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(*((0.08, 0.13, 0.28) if xray else (0.97, 0.95, 0.92)))
    ctx.paint()
    micro = Micro(items, R, seed)
    micro.draw(ctx, max(t - (0.0 if cont else 0.2), 0))
    # brillo de cristal
    ctx.arc(-R * 0.35, -R * 0.45, R * 0.35, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.12)
    ctx.fill()
    ctx.restore()
    ctx.arc(0, 0, R + 8, 0, 2 * math.pi)
    ctx.set_source_rgb(0.85, 0.9, 1.0)
    ctx.set_line_width(10)
    ctx.stroke()
    ctx.restore()

    # etiquetas con flecha, una a una
    tt = max(t - 0.2, 0)
    for n, it in enumerate(items):
        lab = (it.get("label") or "").upper()[:18]
        if not lab:
            continue
        a = 1.0 if cont else ease((t - 0.45 - n * 0.3) / 0.25)
        if a <= 0:
            continue
        sx, sy = LABEL_SPOTS[n]
        lx, ly = cx + sx * R * 0.72, cy + sy * R
        px, py = micro.anchor(it, tt, (sx, sy))
        tx, ty = cx + px * k, cy + py * k
        ctx.move_to(lx, ly + (32 if sy < 0 else -32))
        ctx.line_to(lx + (tx - lx) * a, ly + (ty - ly) * a)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(6)
        ctx.stroke()
        ctx.arc(tx, ty, 9 * a, 0, 2 * math.pi)
        ctx.fill()
        ctx.save()
        ctx.translate(lx, ly)
        ctx.scale(pop(a * 1.0), pop(a * 1.0))
        _pill(ctx, lab, 0, 0, _col(it))
        ctx.restore()

    title = (spec.get("title") or "").upper()[:26]
    if title:
        a = ease((t - 0.5) / 0.3)
        if a > 0:
            _text(ctx, title, cx, cy - R - 120, 52, fill=(1, 1, 1), lw=10, max_w=900)


# ---------------------------------------------------------------- gráficas
def fmt_num(v):
    if abs(v) >= 100 or float(v).is_integer():
        return f"{int(round(v)):,}".replace(",", ".")
    txt = f"{v:.1f}" if abs(v) >= 1 else f"{v:.2f}"
    return txt.rstrip("0").rstrip(".").replace(".", ",") if "." in txt else txt


def _panel(ctx, x0, y0, w, h, r=40):
    ctx.new_path()
    ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
    ctx.arc(x0 + w - r, y0 + h - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y0 + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()
    _outline(ctx, (1, 1, 1), 10)


BAR_COLORS = [(0.35, 0.65, 1.0), (1.0, 0.55, 0.25), (0.35, 0.8, 0.45), (0.85, 0.4, 0.9)]


def draw_chart(ctx, spec, t, center=(540, 760)):
    k = pop((t - 0.3) / 0.4)
    if k <= 0:
        return
    cx, cy = center
    typ = spec.get("type")
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    if typ == "counter":
        to = float(spec.get("to") or 0)
        fr = float(spec.get("from") or 0)
        v = fr + (to - fr) * ease((t - 0.5) / 1.6)
        w, h = 800, 360
        _panel(ctx, -w / 2, -h / 2, w, h)
        num = f"{spec.get('prefix', '')}{fmt_num(v)}{spec.get('suffix', '')}"
        _text(ctx, num, 0, -20, 150, fill=(1, 0.8, 0.1), lw=16, max_w=720)
        if spec.get("title"):
            _font(ctx, 46)
            _text(ctx, str(spec["title"]).upper()[:30], 0, 120, 46, fill=INK, stroke=None, max_w=720)
    else:
        items = [i for i in (spec.get("items") or []) if isinstance(i.get("value"), (int, float))][:4]
        if not items:
            ctx.restore()
            return
        n = len(items)
        w, h = 800, 150 + n * 130
        _panel(ctx, -w / 2, -h / 2, w, h)
        top = -h / 2 + 40
        if spec.get("title"):
            _text(ctx, str(spec["title"]).upper()[:30], 0, top + 30, 48, fill=INK, stroke=None, max_w=720)
        mx = max(abs(i["value"]) for i in items) or 1
        unit = spec.get("unit", "")
        for j, it in enumerate(items):
            y = top + 115 + j * 130
            _text(ctx, str(it.get("label", ""))[:16], -w / 2 + 40, y - 38, 40, fill=INK, stroke=None, anchor="l")
            g = ease((t - 0.6 - j * 0.25) / 1.0)
            bw = (w - 80) * 0.62 * abs(it["value"]) / mx * g
            x0 = -w / 2 + 40
            ctx.new_path()
            ctx.rectangle(x0, y, max(bw, 4), 56)
            _outline(ctx, BAR_COLORS[j % 4], 6)
            if g > 0:
                _text(ctx, f"{fmt_num(it['value'] * g)}{(' ' + unit) if unit else ''}", x0 + bw + 20, y + 28, 42,
                      fill=INK, stroke=None, anchor="l")
    ctx.restore()


def _num(v):
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) if v == v and abs(v) != float("inf") else None
    txt = str(v).strip().replace(" ", "").replace("\u00a0", "")
    if "," in txt or txt.count(".") > 1 or (txt.count(".") == 1 and len(txt.split(".")[1]) == 3):
        txt = txt.replace(".", "").replace(",", ".")  # formato español: 86.000.000.000 o 1,4
    try:
        return float(txt)
    except ValueError:
        return None


def _safe(fn):
    def wrapper(v):
        try:
            return fn(v)
        except Exception:
            return None
    return wrapper


def _txt_(v, n):
    return v[:n] if isinstance(v, str) else ""


@_safe
def clean_zoom(z):
    if not isinstance(z, dict) or not isinstance(z.get("items"), list):
        return None
    items = []
    for it in (z.get("items") or [])[:4]:
        if not isinstance(it, dict) or not isinstance(it.get("kind"), str) or it["kind"] not in KINDS:
            continue
        do = it["do"] if isinstance(it.get("do"), str) and it["do"] in DOS[it["kind"]] else DOS[it["kind"]][0]
        col = it["color"] if isinstance(it.get("color"), str) and it["color"] in COLORS else None
        items.append({"kind": it["kind"], "label": _txt_(it.get("label"), 18).upper(), "do": do, "color": col})
    if not items:
        return None
    return {"of": _txt_(z.get("of"), 20).lower(), "items": items}


@_safe
def clean_chart(c):
    if not isinstance(c, dict):
        return None
    if c.get("type") == "counter":
        to = _num(c.get("to"))
        if to is None:
            return None
        return {"type": "counter", "to": to, "from": _num(c.get("from")) or 0,
                "prefix": _txt_(c.get("prefix"), 4), "suffix": _txt_(c.get("suffix"), 8),
                "title": _txt_(c.get("title"), 30)}
    items = []
    for it in (c.get("items") if isinstance(c.get("items"), list) else [])[:4]:
        v = _num(it.get("value")) if isinstance(it, dict) else None
        if v is not None and abs(v) < 1e15:
            items.append({"label": _txt_(it.get("label"), 16), "value": v})
    if len(items) < 2 or not any(i["value"] for i in items):
        return None
    return {"type": "bars", "items": items, "unit": _txt_(c.get("unit"), 8), "title": _txt_(c.get("title"), 30)}
