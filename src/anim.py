"""Motor de animación por código: monigotes con esqueleto, objetos y textos animados.

Cada escena se describe con un dict:
  {"action": "shocked", "expression": "shocked", "props": ["heart", "heart"],
   "keyword": "3 CORAZONES", "second": "scared", "bg": "azul"}
y se dibuja fotograma a fotograma con cairo (vectorial, suavizado), sin ninguna API.
"""
import math
import random
import subprocess

import cairo

import config

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS
INK = (0.11, 0.11, 0.13)
WHITE = (1, 1, 1)

BACKGROUNDS = {
    "azul": (0.78, 0.89, 1.00), "amarillo": (1.00, 0.94, 0.70), "rosa": (1.00, 0.84, 0.89),
    "verde": (0.80, 0.95, 0.83), "morado": (0.87, 0.83, 1.00), "naranja": (1.00, 0.86, 0.72),
    "rojo": (1.00, 0.78, 0.76), "gris": (0.90, 0.91, 0.93),
}
SHIRTS = [(0.95, 0.33, 0.30), (0.20, 0.55, 0.95), (0.20, 0.72, 0.45), (0.98, 0.66, 0.15), (0.62, 0.38, 0.90)]

ACTIONS = ["idle", "talk", "walk", "run", "jump", "shocked", "point", "think", "celebrate", "scared",
           "sad", "wave", "angry", "shrug", "laugh"]
EXPRESSIONS = ["happy", "neutral", "shocked", "sad", "scared", "thinking", "angry"]
DEFAULT_EXPR = {"shocked": "shocked", "scared": "scared", "sad": "sad", "think": "thinking",
                "celebrate": "happy", "jump": "happy", "angry": "angry", "laugh": "happy", "wave": "happy",
                "point": "happy", "shrug": "neutral", "walk": "neutral", "run": "scared", "talk": "neutral"}


# ---------------------------------------------------------------- utilidades
def ease_out_back(x, k=1.9):
    x = min(max(x, 0.0), 1.0) - 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def shade(c, f):
    return tuple(min(max(v * f, 0), 1) for v in c)


# ---------------------------------------------------------------- poses
def pose_for(action, t, seed=0.0):
    """Devuelve ángulos (radianes, 0 = hacia abajo, + = hacia delante) y desplazamientos."""
    s = math.sin
    p = dict(tilt=0.0, ba1=0.25, ba2=0.25, fa1=0.25, fa2=0.25,
             bl1=-0.12, bl2=0.05, fl1=0.12, fl2=-0.05, y=0.0, dx=0.0, head=0.0, shake=0.0, mirror=True)
    breathe = s(t * 2.4 + seed)
    p["ba1"] += 0.05 * breathe
    p["fa1"] -= 0.05 * breathe
    p["y"] = 4 * breathe

    if action == "talk":
        p["fa1"] = 0.9 + 0.35 * s(t * 5 + seed)
        p["fa2"] = 1.1 + 0.3 * s(t * 3.3)
        p["head"] = 0.06 * s(t * 4)
    elif action in ("walk", "run"):
        f = 8 if action == "walk" else 13
        a = 0.5 if action == "walk" else 0.8
        sw = s(t * f)
        p.update(fl1=a * sw, fl2=-0.5 - 0.4 * max(0, -sw), bl1=-a * sw, bl2=-0.5 - 0.4 * max(0, sw),
                 fa1=-0.6 * sw, fa2=0.6, ba1=0.6 * sw, ba2=0.6, y=-abs(s(t * f)) * 18,
                 tilt=0.08 if action == "walk" else 0.22, mirror=False)
        if action == "run":
            p.update(fa2=1.4, ba2=1.4)
    elif action == "jump":
        ph = (t * 1.4) % 1.0
        air = s(math.pi * ph)
        p.update(y=-260 * air, ba1=2.6 - 0.4 * (1 - air), fa1=2.7 - 0.4 * (1 - air), ba2=0.2, fa2=0.2,
                 fl1=0.6 * air, fl2=-1.2 * air, bl1=0.3 * air, bl2=-1.0 * air)
    elif action == "shocked":
        j = s(t * 40) * (1 if t < 0.5 else 0.2)
        p.update(ba1=2.5 + 0.08 * j, fa1=2.4 - 0.08 * j, ba2=0.5, fa2=0.5, tilt=-0.12,
                 y=-30 * ease_out(t * 4) * (1 - min(t, 1)), shake=1.0 if t < 0.35 else 0.0)
    elif action == "point":
        p.update(fa1=1.55 + 0.05 * s(t * 3), fa2=0.0, ba1=0.5, ba2=-1.9, tilt=-0.04)
    elif action == "think":
        p.update(fa1=0.55, fa2=2.5, ba1=0.7, ba2=1.6, head=0.12 + 0.04 * s(t * 1.5), tilt=-0.03)
    elif action == "celebrate":
        ph = (t * 2.2) % 1.0
        p.update(y=-90 * s(math.pi * ph), ba1=2.7 + 0.25 * s(t * 12), fa1=2.7 - 0.25 * s(t * 12),
                 ba2=0.3 * s(t * 9), fa2=-0.3 * s(t * 9))
    elif action == "scared":
        j = s(t * 55)
        p.update(fa1=1.3 + 0.05 * j, fa2=1.3, ba1=1.2 - 0.05 * j, ba2=1.4, fl1=0.35, fl2=-0.7,
                 bl1=-0.05, bl2=-0.6, tilt=-0.1 + 0.015 * j, dx=3 * j)
    elif action == "sad":
        p.update(tilt=0.18, ba1=0.08, fa1=0.08, ba2=0.05, fa2=0.05, head=0.25, y=6 + 3 * s(t))
    elif action == "wave":
        p.update(fa1=2.5, fa2=0.4 + 0.6 * s(t * 9), ba1=0.3)
    elif action == "angry":
        st = abs(s(t * 6))
        p.update(fa1=1.0, fa2=1.8, ba1=1.0, ba2=1.8, tilt=0.1, y=-25 * st, shake=0.4)
    elif action == "shrug":
        k = ease_out((t % 1.6) / 0.4) * (1 - ease_out(((t % 1.6) - 0.9) / 0.4))
        p.update(fa1=0.9, fa2=-1.9 * k - 0.2, ba1=0.9, ba2=-1.9 * k - 0.2, head=0.15 * k)
    elif action == "laugh":
        b = s(t * 14)
        p.update(tilt=-0.15 + 0.06 * b, ba1=0.9, ba2=1.5, fa1=0.9, fa2=1.5, y=8 * b, head=-0.15)
    return p


# ---------------------------------------------------------------- personaje
def _limb(ctx, ox, oy, a1, a2, l1, l2, facing):
    x1 = ox + l1 * math.sin(a1) * facing
    y1 = oy + l1 * math.cos(a1)
    a = a1 + a2
    x2 = x1 + l2 * math.sin(a) * facing
    y2 = y1 + l2 * math.cos(a)
    ctx.move_to(ox, oy)
    ctx.line_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()
    return x2, y2


def _leg_drop(a1, a2, l1, l2):
    return l1 * math.cos(a1) + l2 * math.cos(a1 + a2)


_DARK = False
_HALO = [(dx, dy) for dx in (-7, 0, 7) for dy in (-7, 0, 7) if dx or dy]


def draw_char(ctx, x, feet, sc, *args):
    """Monigote; en paisajes oscuros lleva un halo blanco para que se vea."""
    if not _DARK:
        draw_character(ctx, x, feet, sc, *args)
        return
    ctx.save()
    ctx.rectangle(x - 420 * sc, feet - 1050 * sc, 840 * sc, 1100 * sc)
    ctx.clip()
    ctx.push_group()
    draw_character(ctx, x, feet, sc, *args)
    pat = ctx.pop_group()
    for dx, dy in _HALO:
        ctx.save()
        ctx.translate(dx, dy)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.mask(pat)
        ctx.restore()
    ctx.set_source(pat)
    ctx.paint()
    ctx.restore()


def draw_character(ctx, x, feet, sc, pose, expr, shirt, facing, t, talking, seed):
    UA, LA, UL, LL, TORSO, R = 115 * sc, 105 * sc, 135 * sc, 135 * sc, 200 * sc, 78 * sc
    x += pose["dx"]
    drop = max(_leg_drop(pose["bl1"], pose["bl2"], UL, LL), _leg_drop(pose["fl1"], pose["fl2"], UL, LL))
    hx, hy = x, feet - drop + pose["y"] * sc

    # sombra
    air = max(0.0, -pose["y"]) / 260
    ctx.save()
    ctx.translate(x, feet + 8 * sc)
    ctx.scale(1, 0.22)
    ctx.arc(0, 0, 120 * sc * (1 - 0.4 * air), 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0, 0, 0, 0.13 * (1 - 0.5 * air))
    ctx.fill()

    tilt = pose["tilt"]
    nx = hx + math.sin(tilt) * facing * TORSO
    ny = hy - math.cos(tilt) * TORSO
    sx = hx + math.sin(tilt) * facing * (TORSO - 25 * sc)
    sy = hy - math.cos(tilt) * (TORSO - 25 * sc)

    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    # extremidades traseras
    ctx.set_source_rgb(*shade(INK, 1.9))
    ctx.set_line_width(16 * sc)
    _limb(ctx, hx, hy, pose["bl1"], pose["bl2"], UL, LL, facing)
    _limb(ctx, sx, sy, pose["ba1"], pose["ba2"], UA, LA, -facing if pose["mirror"] else facing)

    # tronco con camiseta
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(58 * sc)
    ctx.move_to(hx, hy)
    ctx.line_to(nx, ny)
    ctx.stroke()
    ctx.set_source_rgb(*shirt)
    ctx.set_line_width(46 * sc)
    ctx.move_to(hx, hy)
    ctx.line_to(nx, ny)
    ctx.stroke()

    # extremidades delanteras
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(16 * sc)
    _limb(ctx, hx, hy, pose["fl1"], pose["fl2"], UL, LL, facing)
    _limb(ctx, sx, sy, pose["fa1"], pose["fa2"], UA, LA, facing)

    # cabeza
    ha = tilt + pose["head"]
    cx = nx + math.sin(ha) * facing * (R + 4 * sc)
    cy = ny - math.cos(ha) * (R + 4 * sc)
    ctx.arc(cx, cy, R, 0, 2 * math.pi)
    ctx.set_source_rgb(*WHITE)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(10 * sc)
    ctx.stroke()
    draw_face(ctx, cx, cy, R, sc, expr, facing, t, talking, seed, ha)


def draw_face(ctx, cx, cy, R, sc, expr, facing, t, talking, seed, ang):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(ang * facing)
    fx = 16 * sc * facing
    ex = 25 * sc
    ey = -10 * sc
    blink = ((t + seed) % 3.1) < 0.12
    big = expr in ("shocked", "scared")
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(7 * sc)
    for side in (-1, 1):
        x = fx + side * ex
        if blink and not big:
            ctx.move_to(x - 8 * sc, ey)
            ctx.line_to(x + 8 * sc, ey)
            ctx.stroke()
        elif big:
            ctx.arc(x, ey, 14 * sc, 0, 2 * math.pi)
            ctx.set_source_rgb(*WHITE)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(5 * sc)
            ctx.stroke()
            ctx.arc(x + 2 * sc * facing, ey, 6 * sc, 0, 2 * math.pi)
            ctx.fill()
        else:
            ctx.arc(x, ey, 8 * sc, 0, 2 * math.pi)
            ctx.fill()
    # cejas
    ctx.set_line_width(6 * sc)
    by = ey - 26 * sc
    for side in (-1, 1):
        x = fx + side * ex
        if expr == "angry":
            ctx.move_to(x - 13 * sc, by - side * 6 * sc)
            ctx.line_to(x + 13 * sc, by + side * 6 * sc)
        elif expr in ("sad", "scared"):
            ctx.move_to(x - 13 * sc, by + side * 6 * sc - 6 * sc)
            ctx.line_to(x + 13 * sc, by - side * 6 * sc - 6 * sc)
        elif expr == "thinking" and side == 1:
            ctx.move_to(x - 12 * sc, by - 10 * sc)
            ctx.line_to(x + 12 * sc, by - 16 * sc)
        elif expr == "shocked":
            ctx.move_to(x - 12 * sc, by - 10 * sc)
            ctx.curve_to(x - 4 * sc, by - 18 * sc, x + 4 * sc, by - 18 * sc, x + 12 * sc, by - 10 * sc)
        else:
            continue
        ctx.stroke()
    # boca
    my = 32 * sc
    mx = fx
    open_ = 0.0
    if talking:
        open_ = max(0.0, math.sin(t * 17 + seed) * 0.6 + math.sin(t * 9.3) * 0.4)
    ctx.set_line_width(7 * sc)
    if expr == "shocked":
        ctx.save()
        ctx.translate(mx, my)
        ctx.scale(1, 1.3 + 0.2 * open_)
        ctx.arc(0, 0, 14 * sc, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    elif expr == "scared":
        ctx.move_to(mx - 22 * sc, my)
        for k in range(1, 7):
            ctx.line_to(mx - 22 * sc + k * 44 * sc / 6, my + (6 if k % 2 else -6) * sc)
        ctx.stroke()
    elif expr == "sad":
        ctx.arc_negative(mx, my + 22 * sc, 20 * sc, -0.4, -math.pi + 0.4)
        ctx.stroke()
    elif expr in ("happy", "neutral") and open_ > 0.15:
        ctx.save()
        ctx.translate(mx, my - 2 * sc)
        ctx.scale(1, 0.25 + 0.75 * open_)
        ctx.arc(0, 0, 18 * sc, 0, math.pi) if expr == "happy" else ctx.arc(0, 0, 14 * sc, 0, 2 * math.pi)
        ctx.close_path()
        ctx.restore()
        ctx.fill()
    elif expr == "happy":
        ctx.arc(mx, my - 12 * sc, 24 * sc, 0.35, math.pi - 0.35)
        ctx.stroke()
    elif expr == "thinking":
        ctx.move_to(mx - 6 * sc, my + 2 * sc)
        ctx.line_to(mx + 18 * sc * facing, my - 4 * sc)
        ctx.stroke()
    elif expr == "angry":
        ctx.move_to(mx - 18 * sc, my + 4 * sc)
        ctx.line_to(mx + 18 * sc, my + 4 * sc)
        ctx.stroke()
    else:
        ctx.move_to(mx - 14 * sc, my)
        ctx.line_to(mx + 14 * sc, my)
        ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- objetos
def _outline(ctx, fill, lw=9):
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(lw)
    ctx.stroke()


def _star_path(ctx, r, n=5, inner=0.45):
    for k in range(n * 2):
        a = -math.pi / 2 + k * math.pi / n
        rr = r if k % 2 == 0 else r * inner
        (ctx.move_to if k == 0 else ctx.line_to)(rr * math.cos(a), rr * math.sin(a))
    ctx.close_path()


def _text_prop(ctx, txt, size, fill):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(txt)
    ctx.move_to(-e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing)
    ctx.text_path(txt)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    _outline(ctx, fill, 12)


def draw_prop(ctx, name, r, t):
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if name == "heart":
        ctx.move_to(0, r * 0.85)
        ctx.curve_to(-r * 1.3, -r * 0.1, -r * 0.55, -r * 1.05, 0, -r * 0.35)
        ctx.curve_to(r * 0.55, -r * 1.05, r * 1.3, -r * 0.1, 0, r * 0.85)
        _outline(ctx, (0.95, 0.25, 0.32))
    elif name == "star":
        _star_path(ctx, r)
        _outline(ctx, (1.0, 0.82, 0.15))
    elif name == "question":
        _text_prop(ctx, "?", r * 2.2, (0.35, 0.55, 1.0))
    elif name == "exclamation":
        _text_prop(ctx, "!", r * 2.2, (1.0, 0.35, 0.25))
    elif name == "bulb":
        ctx.arc(0, -r * 0.25, r * 0.7, math.pi * 0.8, math.pi * 2.2)
        ctx.line_to(r * 0.3, r * 0.55)
        ctx.line_to(-r * 0.3, r * 0.55)
        ctx.close_path()
        _outline(ctx, (1.0, 0.9, 0.3))
        ctx.rectangle(-r * 0.32, r * 0.55, r * 0.64, r * 0.35)
        _outline(ctx, (0.7, 0.72, 0.78))
        for k in range(5):  # rayos
            a = -math.pi / 2 + (k - 2) * 0.55
            ctx.move_to(math.cos(a) * r * 1.05, -r * 0.25 + math.sin(a) * r * 1.05)
            ctx.line_to(math.cos(a) * r * 1.35, -r * 0.25 + math.sin(a) * r * 1.35)
        ctx.set_line_width(8)
        ctx.stroke()
    elif name == "planet":
        ctx.arc(0, 0, r * 0.65, 0, 2 * math.pi)
        _outline(ctx, (0.95, 0.6, 0.3))
        ctx.save()
        ctx.rotate(-0.35)
        ctx.scale(1, 0.28)
        ctx.arc(0, 0, r * 1.15, 0, math.pi)
        ctx.restore()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(9)
        ctx.stroke()
    elif name == "rocket":
        ctx.save()
        ctx.rotate(0.5)
        ctx.move_to(0, -r)
        ctx.curve_to(r * 0.5, -r * 0.5, r * 0.45, r * 0.3, r * 0.35, r * 0.6)
        ctx.line_to(-r * 0.35, r * 0.6)
        ctx.curve_to(-r * 0.45, r * 0.3, -r * 0.5, -r * 0.5, 0, -r)
        _outline(ctx, (0.92, 0.93, 0.97))
        ctx.arc(0, -r * 0.2, r * 0.18, 0, 2 * math.pi)
        _outline(ctx, (0.4, 0.75, 1.0), 6)
        fl = 0.7 + 0.3 * math.sin(t * 30)
        ctx.move_to(-r * 0.25, r * 0.6)
        ctx.line_to(0, r * (0.6 + 0.6 * fl))
        ctx.line_to(r * 0.25, r * 0.6)
        _outline(ctx, (1.0, 0.55, 0.15), 6)
        ctx.restore()
    elif name == "clock":
        ctx.arc(0, 0, r * 0.85, 0, 2 * math.pi)
        _outline(ctx, WHITE)
        ctx.set_line_width(9)
        ctx.move_to(0, 0)
        ctx.line_to(0, -r * 0.55)
        ctx.move_to(0, 0)
        a = t * 3
        ctx.line_to(math.sin(a) * r * 0.65, -math.cos(a) * r * 0.65)
        ctx.stroke()
    elif name in ("coin", "money"):
        ctx.arc(0, 0, r * 0.8, 0, 2 * math.pi)
        _outline(ctx, (1.0, 0.8, 0.2))
        _text_prop(ctx, "$", r * 1.1, (1.0, 0.9, 0.45))
    elif name == "skull":
        ctx.arc(0, -r * 0.15, r * 0.75, math.pi * 0.85, math.pi * 2.15)
        ctx.line_to(r * 0.4, r * 0.75)
        ctx.line_to(-r * 0.4, r * 0.75)
        ctx.close_path()
        _outline(ctx, (0.96, 0.96, 0.92))
        ctx.set_source_rgb(*INK)
        for sx in (-1, 1):
            ctx.arc(sx * r * 0.3, -r * 0.1, r * 0.2, 0, 2 * math.pi)
            ctx.fill()
    elif name == "bolt":
        pts = [(0.15, -1), (-0.5, 0.1), (-0.05, 0.1), (-0.2, 1), (0.5, -0.15), (0.05, -0.15)]
        for k, (a, b) in enumerate(pts):
            (ctx.move_to if k == 0 else ctx.line_to)(a * r, b * r)
        ctx.close_path()
        _outline(ctx, (1.0, 0.85, 0.1))
    elif name == "fire":
        w = 1 + 0.06 * math.sin(t * 18)
        ctx.move_to(0, -r * w)
        ctx.curve_to(r * 0.9, -r * 0.2, r * 0.8, r * 0.9, 0, r * 0.9)
        ctx.curve_to(-r * 0.8, r * 0.9, -r * 0.9, -r * 0.2, 0, -r * w)
        _outline(ctx, (1.0, 0.45, 0.15))
        ctx.move_to(0, -r * 0.2)
        ctx.curve_to(r * 0.45, r * 0.2, r * 0.4, r * 0.85, 0, r * 0.85)
        ctx.curve_to(-r * 0.4, r * 0.85, -r * 0.45, r * 0.2, 0, -r * 0.2)
        ctx.set_source_rgb(1.0, 0.85, 0.25)
        ctx.fill()
    elif name == "drop":
        ctx.move_to(0, -r)
        ctx.curve_to(r * 0.9, 0, r * 0.75, r * 0.85, 0, r * 0.85)
        ctx.curve_to(-r * 0.75, r * 0.85, -r * 0.9, 0, 0, -r)
        _outline(ctx, (0.25, 0.55, 1.0))
    elif name == "globe":
        ctx.arc(0, 0, r * 0.85, 0, 2 * math.pi)
        _outline(ctx, (0.35, 0.65, 1.0))
        ctx.set_source_rgb(0.3, 0.78, 0.4)
        for (a, b, c) in [(-0.3, -0.25, 0.32), (0.35, 0.2, 0.28), (-0.1, 0.45, 0.18)]:
            ctx.arc(a * r, b * r, c * r, 0, 2 * math.pi)
            ctx.fill()
        ctx.arc(0, 0, r * 0.85, 0, 2 * math.pi)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(9)
        ctx.stroke()
    elif name == "eye":
        ctx.move_to(-r, 0)
        ctx.curve_to(-r * 0.4, -r * 0.75, r * 0.4, -r * 0.75, r, 0)
        ctx.curve_to(r * 0.4, r * 0.75, -r * 0.4, r * 0.75, -r, 0)
        _outline(ctx, WHITE)
        ctx.arc(r * 0.1 * math.sin(t * 2), 0, r * 0.32, 0, 2 * math.pi)
        _outline(ctx, (0.3, 0.6, 0.9), 6)
    elif name == "magnifier":
        ctx.arc(-r * 0.15, -r * 0.15, r * 0.55, 0, 2 * math.pi)
        _outline(ctx, (0.85, 0.95, 1.0))
        ctx.set_line_width(r * 0.22)
        ctx.move_to(r * 0.25, r * 0.25)
        ctx.line_to(r * 0.85, r * 0.85)
        ctx.set_source_rgb(*INK)
        ctx.stroke()
    elif name == "crown":
        ctx.move_to(-r, r * 0.5)
        for a, b in [(-r, -r * 0.5), (-r * 0.5, 0), (0, -r * 0.7), (r * 0.5, 0), (r, -r * 0.5), (r, r * 0.5)]:
            ctx.line_to(a, b)
        ctx.close_path()
        _outline(ctx, (1.0, 0.8, 0.15))
    elif name == "bomb":
        ctx.arc(0, r * 0.15, r * 0.7, 0, 2 * math.pi)
        _outline(ctx, (0.25, 0.25, 0.3))
        ctx.move_to(r * 0.35, -r * 0.4)
        ctx.curve_to(r * 0.5, -r * 0.8, r * 0.8, -r * 0.7, r * 0.75, -r * 0.95)
        ctx.set_line_width(8)
        ctx.stroke()
        ctx.save()
        ctx.translate(r * 0.75, -r * 0.98)
        ctx.rotate(t * 8)
        _star_path(ctx, r * 0.28 * (1 + 0.2 * math.sin(t * 25)), 6, 0.4)
        ctx.restore()
        ctx.set_source_rgb(1.0, 0.7, 0.1)
        ctx.fill()
    elif name in ("arrow_up", "arrow_down"):
        ctx.save()
        if name == "arrow_down":
            ctx.rotate(math.pi)
        for a, b in [(0, -1), (0.75, -0.1), (0.3, -0.1), (0.3, 0.9), (-0.3, 0.9), (-0.3, -0.1), (-0.75, -0.1)]:
            ctx.line_to(a * r, b * r)
        ctx.close_path()
        ctx.restore()
        _outline(ctx, (0.25, 0.8, 0.4) if name == "arrow_up" else (0.95, 0.3, 0.3))
    elif name == "tree":
        ctx.rectangle(-r * 0.15, r * 0.2, r * 0.3, r * 0.8)
        _outline(ctx, (0.6, 0.38, 0.2))
        ctx.arc(0, -r * 0.2, r * 0.7, 0, 2 * math.pi)
        _outline(ctx, (0.3, 0.75, 0.35))
    elif name == "book":
        ctx.rectangle(-r * 0.8, -r * 0.6, r * 1.6, r * 1.2)
        _outline(ctx, (0.4, 0.5, 0.95))
        ctx.move_to(0, -r * 0.6)
        ctx.line_to(0, r * 0.6)
        ctx.set_line_width(8)
        ctx.stroke()
    elif name == "brain":
        for (a, b, c) in [(-0.35, -0.2, 0.45), (0.3, -0.25, 0.45), (-0.4, 0.25, 0.4), (0.35, 0.25, 0.42), (0, 0, 0.45)]:
            ctx.new_sub_path()
            ctx.arc(a * r, b * r, c * r, 0, 2 * math.pi)
        ctx.set_source_rgb(1.0, 0.68, 0.78)
        ctx.fill()
        for (a, b, c) in [(-0.35, -0.2, 0.45), (0.3, -0.25, 0.45), (-0.4, 0.25, 0.4), (0.35, 0.25, 0.42)]:
            ctx.arc(a * r, b * r, c * r, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
    else:  # desconocido -> estrella
        _star_path(ctx, r)
        _outline(ctx, (1.0, 0.82, 0.15))


PROPS = ["heart", "star", "question", "exclamation", "bulb", "planet", "rocket", "clock", "money",
         "skull", "bolt", "fire", "drop", "globe", "eye", "magnifier", "crown", "bomb", "arrow_up",
         "arrow_down", "tree", "book", "brain"]

PROP_SLOTS = {
    1: [(770, 860)],
    2: [(720, 720), (840, 1010)],
    3: [(690, 660), (880, 860), (700, 1060)],
}


# ---------------------------------------------------------------- texto
def draw_keyword(ctx, text, t, y=400):
    if not text:
        return
    k = ease_out_back(t / 0.35)
    if k <= 0:
        return
    ctx.save()
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    size = 135
    ctx.set_font_size(size)
    e = ctx.text_extents(text)
    if e.width > 940:
        size *= 940 / e.width
        ctx.set_font_size(size)
        e = ctx.text_extents(text)
    ctx.translate(W / 2, y + 6 * math.sin(t * 3))
    ctx.rotate(-0.04 + 0.015 * math.sin(t * 2))
    ctx.scale(k, k)
    ctx.move_to(-e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing)
    ctx.text_path(text)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(26)
    ctx.stroke_preserve()
    ctx.set_source_rgb(1, 0.86, 0.1)
    ctx.fill()
    ctx.restore()


# ---------------------------------------------------------------- escena
FEET = 1380


def draw_scene(ctx, sc, t, dur, idx):
    from src import scenery
    land = sc.get("scene") if sc.get("scene") in scenery.LANDSCAPES else None
    global _DARK
    _DARK = land in scenery.DARK
    bg = BACKGROUNDS.get(sc.get("bg"), BACKGROUNDS["azul"])
    rnd = random.Random(idx * 7919)
    if land:
        scenery.draw_landscape(ctx, land, t, FEET)
    # fondo + suelo + puntitos que se mueven
    if not land:
        ctx.set_source_rgb(*bg)
        ctx.paint()
        ctx.set_source_rgba(1, 1, 1, 0.35)
        for k in range(26):
            px = (rnd.uniform(0, W) + t * 25 * (1 + k % 3)) % (W + 60) - 30
            py = rnd.uniform(0, FEET - 100)
            ctx.arc(px, py, rnd.uniform(6, 16), 0, 2 * math.pi)
            ctx.fill()
        ctx.rectangle(0, FEET, W, H - FEET)
        ctx.set_source_rgb(*shade(bg, 0.9))
        ctx.fill()
        ctx.move_to(0, FEET)
        ctx.line_to(W, FEET)
        ctx.set_source_rgb(*shade(bg, 0.75))
        ctx.set_line_width(6)
        ctx.stroke()

    action = sc.get("action", "talk")
    expr = sc.get("expression") or DEFAULT_EXPR.get(action, "neutral")
    second = sc.get("second")
    props = sc.get("props") or []

    # cámara: zoom lento + sacudida
    pose = pose_for(action, t, idx)
    z = 1.0 + 0.04 * t / max(dur, 0.1)
    shake = pose["shake"]
    ox = shake * 14 * math.sin(t * 61)
    oy = shake * 10 * math.cos(t * 53)
    ctx.save()
    ctx.translate(W / 2 + ox, H * 0.55 + oy)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H * 0.55)

    shirt = SHIRTS[sc.get("shirt", idx) % len(SHIRTS)]
    pop = 0.8 + 0.2 * ease_out_back(t / 0.3)  # pequeño "boing" al entrar

    from src import catalog, creatures, explain  # noqa: F401  (catalog registra todos los modelos)
    creature = sc.get("creature") if sc.get("creature") in creatures.CREATURES else None
    sticker = None if creature else _load_sticker(sc.get("_sticker"))
    from src import emoji
    icon = sc.get("icon") if not creature and sc.get("icon") else None
    zoom = sc.get("zoom") if isinstance(sc.get("zoom"), dict) and sc["zoom"].get("items") else None
    chart = sc.get("chart") if isinstance(sc.get("chart"), dict) and sc["chart"].get("type") else None
    nscale = 1.15
    cr_x, cr_scale = 770, 0.85
    if zoom or chart:
        second, props = "", []
        cr_x, cr_scale = 860, 0.6
    if creature:  # criatura animada por código (con rayos X opcional) en el lado derecho
        second = ""
        props = props[:1]
        creatures.draw_creature(ctx, creature, t + (2.0 if sc.get("_cont") else 0.0), cr_x, FEET, cr_scale,
                                xray_t=0.3 if sc.get("xray") else None, shake=shake)
    elif sticker is not None:  # dibujo de IA para temas que no están en el catálogo
        second = ""
        props = props[:1]
        _draw_sticker(ctx, sticker, t, shake)
    elif icon and not (zoom or chart):  # icono de la biblioteca como protagonista
        second = ""
        props = props[:1]
        kk = ease_out_back((t - 0.05) / 0.45)
        if kk > 0:
            ctx.save()
            ctx.translate(770, FEET + 10)
            ctx.scale(1, 0.2)
            ctx.arc(0, 0, 170 * kk, 0, 2 * math.pi)
            ctx.restore()
            ctx.set_source_rgba(0, 0, 0, 0.15)
            ctx.fill()
            emoji.draw(ctx, icon, 770, FEET - 260, 480, t, k=kk, shake=shake,
                       lively=emoji.group(icon) in ("Animals & Nature", "People & Body", "Smileys & Emotion"))

    if chart:
        mx, facing, nscale = 110, 1, 0.75
    elif zoom:
        mx, facing, nscale = 170, 1, 1.0
    elif creature or sticker is not None or icon:
        mx, facing = 290, 1
    elif second:
        mx, facing = 300, 1
    elif props:
        mx, facing = 330, 1
    else:
        mx, facing = 540, 1 if idx % 2 == 0 else -1
    if action in ("walk", "run") and not (zoom or chart):
        speed = 220 if action == "walk" else 420
        mx = (-160 + speed * t) if not props else min(-160 + speed * t, mx)
        facing = 1

    # objetos (aparecen con rebote, escalonados)
    slots = PROP_SLOTS.get(min(len(props), 3), [])
    if second:
        slots = [(540, 640), (400, 560), (680, 560)][: len(slots)]
    if creature or sticker is not None or icon:
        slots = [(450, 600)]
    for k, (name, (px, py)) in enumerate(zip(props[:3], slots)):
        kk = ease_out_back((t - 0.2 - 0.28 * k) / 0.35)
        if kk <= 0:
            continue
        ctx.save()
        ctx.translate(px, py + 14 * math.sin(t * 2.5 + k))
        ctx.rotate(0.12 * math.sin(t * 1.8 + k * 2))
        ctx.scale(kk, kk)
        size = 95 if (len(props) > 1 or creature or sticker is not None or icon) else 135
        if str(name).startswith("emoji:"):
            emoji.draw(ctx, name[6:], 0, 0, size * 2.1, t)
        else:
            draw_prop(ctx, name, size, t)
        ctx.restore()

    # personajes
    ctx.save()
    ctx.translate(mx, FEET)
    ctx.scale(pop, pop)
    ctx.translate(-mx, -FEET)
    draw_char(ctx, mx, FEET, nscale, pose, expr, shirt, facing, t, True, idx * 1.7)
    ctx.restore()
    if zoom:  # lupa que muestra el proceso por dentro
        anchor = None
        if creature:
            anchor = creatures.part_point(creature, zoom.get("of", ""), t, cr_x, FEET, cr_scale)
        explain.draw_zoom(ctx, zoom, t, (550, 810), 250, anchor=anchor, xray=bool(sc.get("xray")), seed=idx + 1,
                          cont=bool(sc.get("_cont")))
    if chart:
        explain.draw_chart(ctx, chart, t, (610, 800))
    if second:
        p2 = pose_for(second, t, idx + 3.3)
        e2 = DEFAULT_EXPR.get(second, "neutral")
        k2 = ease_out_back((t - 0.15) / 0.3)
        if k2 > 0:
            ctx.save()
            ctx.translate(790, FEET)
            ctx.scale(k2 * 0.92, k2 * 0.92)
            ctx.translate(-790, -FEET)
            draw_char(ctx, 790, FEET, 1.05, p2, e2, SHIRTS[(idx + 2) % len(SHIRTS)], -1, t, False, idx * 3.1)
            ctx.restore()
    ctx.restore()

    if not (isinstance(sc.get("chart"), dict) and sc["chart"].get("type")):
        draw_keyword(ctx, sc.get("keyword", ""), t - 0.1)


_STICKERS = {}


def _load_sticker(path):
    if not path:
        return None
    if path not in _STICKERS:
        try:
            _STICKERS[path] = cairo.ImageSurface.create_from_png(path)
        except Exception as e:
            print(f"[pegatina] no se pudo cargar {path}: {e}")
            _STICKERS[path] = None
    return _STICKERS[path]


def _draw_sticker(ctx, surf, t, shake):
    """Pegatina que entra rebotando, 'respira' y se balancea apoyada en el suelo."""
    sw, sh = surf.get_width(), surf.get_height()
    fit = min(560 / sw, 700 / sh)
    k = ease_out_back((t - 0.05) / 0.4)
    if k <= 0:
        return
    squash = 1 + 0.035 * math.sin(t * 4.2)
    cx, base = 775, FEET + 30
    ctx.save()
    ctx.translate(cx + shake * 10 * math.sin(t * 70), base - 10 * abs(math.sin(t * 2.1)))
    ctx.rotate(0.05 * math.sin(t * 1.9))
    ctx.scale(fit * k / squash, fit * k * squash)
    ctx.set_source_surface(surf, -sw / 2, -sh)
    ctx.paint()
    ctx.restore()


def render_silent(scenes: list, durations: list, out_mp4: str):
    """Dibuja todas las escenas y las codifica en un mp4 sin audio (transición deslizante)."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    tmp = out_mp4[:-4] + ".part.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", tmp],
        stdin=subprocess.PIPE,
    )
    TR = 0.2
    # escenas seguidas con la misma criatura y lupa: continúan sin volver a aparecer desde cero
    for i in range(1, len(scenes)):
        a, b = scenes[i - 1], scenes[i]
        za, zb = a.get("zoom") or {}, b.get("zoom") or {}
        b["_cont"] = bool(zb and za and a.get("creature") == b.get("creature") and za.get("of") == zb.get("of"))
    for i, (sc, dur) in enumerate(zip(scenes, durations)):
        frames = max(int(round(dur * FPS)), 1)
        for f in range(frames):
            t = f / FPS
            if i > 0 and t < TR and not sc.get("_cont"):  # la escena anterior sale por la izquierda
                k = ease_out(t / TR)
                ctx.save()
                ctx.translate(-W * k, 0)
                draw_scene(ctx, scenes[i - 1], durations[i - 1] + t, durations[i - 1], i - 1)
                ctx.restore()
                ctx.save()
                ctx.translate(W * (1 - k), 0)
                draw_scene(ctx, sc, t, dur, i)
                ctx.restore()
            else:
                draw_scene(ctx, sc, t, dur, i)
            surf.flush()
            proc.stdin.write(bytes(surf.get_data()))
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg falló al codificar la animación")
    import os
    os.replace(tmp, out_mp4)
