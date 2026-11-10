"""Paisajes animados de fondo (sustituyen al color plano). Lienzo 1080x1920, suelo en FEET."""
import math
import random

import cairo

W, H = 1080, 1920
INK = (0.11, 0.11, 0.13)


# ---------------------------------------------------------------- utilidades
def sky(ctx, top, bottom, y1=None):
    g = cairo.LinearGradient(0, 0, 0, y1 or H)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bottom)
    ctx.set_source(g)
    ctx.paint()


def ground(ctx, feet, color, line=None, y=None):
    y = feet if y is None else y
    ctx.rectangle(0, y, W, H - y)
    ctx.set_source_rgb(*color)
    ctx.fill()
    ctx.move_to(0, y)
    ctx.line_to(W, y)
    ctx.set_source_rgb(*(line or [c * 0.8 for c in color]))
    ctx.set_line_width(6)
    ctx.stroke()


def hills(ctx, base, amp, freq, color, phase=0.0, outline=True):
    ctx.move_to(0, H)
    for x in range(0, W + 21, 20):
        y = base - amp * (0.6 * math.sin(x * freq + phase) + 0.4 * math.sin(x * freq * 2.3 + phase * 1.7))
        ctx.line_to(x, y)
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.set_source_rgb(*color)
    ctx.fill_preserve() if outline else ctx.fill()
    if outline:
        ctx.set_source_rgba(*INK, 0.35)
        ctx.set_line_width(5)
        ctx.stroke()


def cloud(ctx, x, y, s, color=(1, 1, 1), alpha=0.95):
    for dx, dy, r in ((-60, 10, 50), (-10, -20, 65), (50, 0, 55), (95, 15, 40), (20, 25, 50)):
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
    ctx.set_source_rgba(*color, alpha)
    ctx.fill()


def clouds(ctx, t, n=4, y0=250, y1=800, speed=18, seed=1, color=(1, 1, 1), alpha=0.9):
    rnd = random.Random(seed)
    for k in range(n):
        s = rnd.uniform(0.7, 1.4)
        x = (rnd.uniform(0, W) + t * speed * s) % (W + 400) - 200
        cloud(ctx, x, rnd.uniform(y0, y1), s, color, alpha)


def sun(ctx, x, y, r, t, color=(1.0, 0.85, 0.25)):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(t * 0.3)
    for k in range(12):
        ctx.rotate(math.pi / 6)
        ctx.move_to(r * 1.15, 0)
        ctx.line_to(r * 1.5 + 8 * math.sin(t * 3 + k), 0)
    ctx.set_source_rgba(*color, 0.8)
    ctx.set_line_width(14)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(*color)
    ctx.fill()


def moon(ctx, x, y, r, bgc):
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(0.97, 0.95, 0.85)
    ctx.fill()
    ctx.arc(x + r * 0.45, y - r * 0.2, r * 0.85, 0, 2 * math.pi)
    ctx.set_source_rgb(*bgc)
    ctx.fill()


def stars(ctx, t, n=70, y1=1200, seed=3):
    rnd = random.Random(seed)
    for k in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, y1)
        a = 0.4 + 0.6 * abs(math.sin(t * rnd.uniform(1, 3) + k))
        ctx.arc(x, y, rnd.uniform(2, 5), 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 0.9, a)
        ctx.fill()


def rect(ctx, x, y, w, h, fill, lw=6, alpha=1.0):
    ctx.rectangle(x, y, w, h)
    ctx.set_source_rgba(*fill, alpha)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.6 * alpha)
    ctx.set_line_width(lw)
    ctx.stroke()


def tree_round(ctx, x, base, s, t, color=(0.3, 0.7, 0.35)):
    rect(ctx, x - 14 * s, base - 120 * s, 28 * s, 120 * s, (0.55, 0.36, 0.2))
    sw = 4 * math.sin(t * 1.5 + x)
    for dx, dy, r in ((0, -190, 80), (-55, -150, 60), (55, -150, 60)):
        ctx.new_sub_path()
        ctx.arc(x + (dx + sw) * s, base + dy * s, r * s, 0, 2 * math.pi)
    ctx.set_source_rgb(*color)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.5)
    ctx.set_line_width(5)
    ctx.stroke()


def pine(ctx, x, base, s, color=(0.18, 0.5, 0.32), snow=False):
    rect(ctx, x - 10 * s, base - 40 * s, 20 * s, 40 * s, (0.45, 0.3, 0.18), 4)
    for k in range(3):
        y = base - 40 * s - k * 60 * s
        w = (90 - k * 22) * s
        ctx.move_to(x - w, y)
        ctx.line_to(x, y - 110 * s)
        ctx.line_to(x + w, y)
        ctx.close_path()
        ctx.set_source_rgb(*color)
        ctx.fill_preserve()
        ctx.set_source_rgba(*INK, 0.45)
        ctx.set_line_width(4)
        ctx.stroke()
        if snow:
            ctx.move_to(x - w * 0.35, y - 70 * s)
            ctx.line_to(x, y - 110 * s)
            ctx.line_to(x + w * 0.35, y - 70 * s)
            ctx.close_path()
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()


def palm(ctx, x, base, s, t):
    sway = 0.06 * math.sin(t * 1.4)
    ctx.save()
    ctx.translate(x, base)
    ctx.rotate(sway)
    ctx.move_to(0, 0)
    ctx.curve_to(20 * s, -150 * s, 10 * s, -300 * s, 40 * s, -420 * s)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(40 * s)
    ctx.stroke_preserve()
    ctx.set_source_rgb(0.65, 0.45, 0.25)
    ctx.set_line_width(28 * s)
    ctx.stroke()
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.55 + 0.08 * math.sin(t * 2 + k)
        ctx.move_to(40 * s, -420 * s)
        ctx.curve_to(40 * s + math.cos(a) * 120 * s, -420 * s + math.sin(a) * 120 * s - 40 * s,
                     40 * s + math.cos(a) * 200 * s, -420 * s + math.sin(a) * 160 * s,
                     40 * s + math.cos(a) * 230 * s, -420 * s + math.sin(a) * 200 * s + 60 * s)
        ctx.set_source_rgb(0.25, 0.68, 0.32)
        ctx.set_line_width(26 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.restore()


def falling(ctx, t, n, color, speed, size, seed=5, wind=0.0, streak=False):
    rnd = random.Random(seed)
    for k in range(n):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        sp = speed * rnd.uniform(0.7, 1.3)
        y = (y0 + t * sp) % (H + 40) - 20
        x = (x0 + wind * t * sp / speed + 20 * math.sin(t + k)) % W
        if streak:
            ctx.move_to(x, y)
            ctx.line_to(x - 6, y + 34)
            ctx.set_source_rgba(*color, 0.7)
            ctx.set_line_width(4)
            ctx.stroke()
        else:
            ctx.arc(x, y, size * rnd.uniform(0.6, 1.3), 0, 2 * math.pi)
            ctx.set_source_rgba(*color, 0.9)
            ctx.fill()


def rising(ctx, t, n, color, speed, size, seed=7, y_from=H, alpha=0.6):
    rnd = random.Random(seed)
    for k in range(n):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        y = y_from - ((H - y0 + t * speed * rnd.uniform(0.7, 1.3)) % H)
        ctx.arc(x0 + 15 * math.sin(t * 2 + k), y, size * rnd.uniform(0.5, 1.4), 0, 2 * math.pi)
        ctx.set_source_rgba(*color, alpha)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, alpha * 0.8)
        ctx.set_line_width(2)
        ctx.stroke()


def building_row(ctx, base, t, colors, seed=2, night=False, hmin=300, hmax=700):
    rnd = random.Random(seed)
    x = -20
    while x < W:
        w = rnd.uniform(110, 190)
        h = rnd.uniform(hmin, hmax)
        c = rnd.choice(colors)
        rect(ctx, x, base - h, w, h, c, 5)
        for wy in range(int(base - h + 30), int(base - 40), 60):
            for wx in range(int(x + 20), int(x + w - 30), 45):
                lit = night and (hash((wx, wy, seed)) % 3 != 0)
                flick = lit and (hash((wx, wy)) % 11 == 0) and math.sin(t * 3 + wx) > 0.6
                ctx.rectangle(wx, wy, 24, 32)
                if lit and not flick:
                    ctx.set_source_rgb(1.0, 0.88, 0.45)
                else:
                    ctx.set_source_rgba(1, 1, 1, 0.35 if not night else 0.08)
                ctx.fill()
        x += w + rnd.uniform(5, 25)


# ---------------------------------------------------------------- paisajes
def L_playa(ctx, t, feet):
    sky(ctx, (0.45, 0.75, 1.0), (0.85, 0.95, 1.0), feet)
    sun(ctx, 860, 330, 90, t)
    clouds(ctx, t, 3, 300, 650)
    sea_y = feet - 260
    ctx.rectangle(0, sea_y, W, 300)
    ctx.set_source_rgb(0.2, 0.6, 0.9)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(6)
    for k in range(4):
        y = sea_y + 40 + k * 55
        ctx.move_to(0, y)
        for x in range(0, W + 1, 20):
            ctx.line_to(x, y + 8 * math.sin(x / 50 + t * 2 + k))
        ctx.stroke()
    ground(ctx, feet - 40, (0.98, 0.88, 0.6))
    palm(ctx, 960, feet - 20, 1.0, t)


def L_mar(ctx, t, feet):
    sky(ctx, (0.25, 0.6, 0.9), (0.05, 0.25, 0.55))
    for k in range(6):  # rayos de luz
        x = 100 + k * 190 + 30 * math.sin(t * 0.5 + k)
        ctx.move_to(x, 0)
        ctx.line_to(x + 80, 0)
        ctx.line_to(x - 120, feet)
        ctx.line_to(x - 220, feet)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.07)
        ctx.fill()
    rising(ctx, t, 30, (0.8, 0.95, 1.0), 80, 9, alpha=0.5)
    ground(ctx, feet, (0.93, 0.85, 0.6))
    for k in range(7):  # algas
        x = 40 + k * 160
        ctx.move_to(x, feet + 10)
        for j in range(1, 9):
            ctx.line_to(x + 25 * math.sin(t * 1.5 + j * 0.6 + k), feet - j * 45)
        ctx.set_source_rgb(0.2, 0.65, 0.35)
        ctx.set_line_width(20)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def L_abismo(ctx, t, feet):
    sky(ctx, (0.03, 0.08, 0.2), (0.0, 0.02, 0.07))
    rnd = random.Random(9)
    for k in range(40):
        x, y = rnd.uniform(0, W), rnd.uniform(0, feet)
        a = 0.3 + 0.7 * abs(math.sin(t * rnd.uniform(0.5, 2) + k))
        ctx.arc(x + 10 * math.sin(t + k), y, rnd.uniform(3, 7), 0, 2 * math.pi)
        ctx.set_source_rgba(0.4, 1.0, 0.9, a)
        ctx.fill()
    ground(ctx, feet, (0.1, 0.12, 0.2))


def L_selva(ctx, t, feet):
    sky(ctx, (0.55, 0.85, 0.6), (0.85, 0.97, 0.75), feet)
    hills(ctx, feet - 400, 60, 0.006, (0.2, 0.55, 0.3), 1)
    hills(ctx, feet - 220, 50, 0.009, (0.15, 0.45, 0.25), 3)
    for k in range(5):  # lianas
        x = 80 + k * 230
        ctx.move_to(x, 0)
        ctx.curve_to(x + 30 * math.sin(t + k), 300, x - 20, 500, x + 15 * math.sin(t * 1.3 + k), 650 + k * 40)
        ctx.set_source_rgb(0.25, 0.5, 0.2)
        ctx.set_line_width(12)
        ctx.stroke()
    for k in range(8):  # hojas grandes en primer plano
        x = k * 150
        ctx.save()
        ctx.translate(x, feet + 40)
        ctx.rotate(-0.4 + k * 0.12 + 0.05 * math.sin(t * 2 + k))
        ctx.move_to(0, 0)
        ctx.curve_to(-60, -100, -30, -230, 0, -260)
        ctx.curve_to(30, -230, 60, -100, 0, 0)
        ctx.set_source_rgb(0.2, 0.62, 0.3)
        ctx.fill()
        ctx.restore()
    ground(ctx, feet + 10, (0.35, 0.28, 0.18))


def L_bosque(ctx, t, feet):
    sky(ctx, (0.6, 0.85, 1.0), (0.9, 0.97, 1.0), feet)
    clouds(ctx, t, 3, 250, 600)
    hills(ctx, feet - 330, 50, 0.007, (0.55, 0.8, 0.55), 0.5)
    for k in range(9):
        pine(ctx, 30 + k * 130, feet - 200, 1.1, (0.25, 0.55, 0.35))
    for k in range(5):
        pine(ctx, 90 + k * 240, feet - 40, 1.5, (0.18, 0.48, 0.3))
    ground(ctx, feet, (0.45, 0.72, 0.38))


def L_desierto(ctx, t, feet):
    sky(ctx, (1.0, 0.75, 0.45), (1.0, 0.92, 0.7), feet)
    sun(ctx, 800, 360, 110, t, (1.0, 0.9, 0.4))
    hills(ctx, feet - 300, 70, 0.004, (0.98, 0.78, 0.45), 2)
    hills(ctx, feet - 150, 50, 0.006, (0.95, 0.72, 0.4), 4)
    for x, s in ((150, 1.0), (930, 0.8)):  # cactus
        rect(ctx, x - 25 * s, feet - 280 * s, 50 * s, 280 * s, (0.3, 0.65, 0.35))
        rect(ctx, x - 90 * s, feet - 220 * s, 30 * s, 100 * s, (0.3, 0.65, 0.35))
        rect(ctx, x + 60 * s, feet - 250 * s, 30 * s, 110 * s, (0.3, 0.65, 0.35))
    ctx.set_source_rgba(1, 1, 1, 0.15)  # calima
    for k in range(5):
        y = feet - 80 - k * 40
        ctx.move_to(0, y)
        for x in range(0, W + 1, 30):
            ctx.line_to(x, y + 6 * math.sin(x / 40 + t * 4 + k))
        ctx.set_line_width(4)
        ctx.stroke()
    ground(ctx, feet, (0.97, 0.82, 0.52))


def L_montana(ctx, t, feet):
    sky(ctx, (0.55, 0.75, 1.0), (0.9, 0.95, 1.0), feet)
    for (x, h, c) in ((250, 900, (0.55, 0.6, 0.7)), (750, 1050, (0.5, 0.55, 0.68)), (1050, 750, (0.6, 0.65, 0.75))):
        ctx.move_to(x - 450, feet)
        ctx.line_to(x, feet - h)
        ctx.line_to(x + 450, feet)
        ctx.close_path()
        ctx.set_source_rgb(*c)
        ctx.fill()
        ctx.move_to(x - 120, feet - h + 260)
        ctx.line_to(x, feet - h)
        ctx.line_to(x + 120, feet - h + 260)
        ctx.line_to(x + 50, feet - h + 220)
        ctx.line_to(x, feet - h + 270)
        ctx.line_to(x - 60, feet - h + 220)
        ctx.close_path()
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    clouds(ctx, t, 3, 500, 800, alpha=0.75)
    for k in range(6):
        pine(ctx, 60 + k * 200, feet, 1.0, snow=True)
    ground(ctx, feet, (0.95, 0.97, 1.0))
    falling(ctx, t, 45, (1, 1, 1), 90, 6)


def L_polo(ctx, t, feet):
    sky(ctx, (0.65, 0.85, 1.0), (0.92, 0.97, 1.0), feet)
    for x, w, h in ((180, 260, 260), (820, 340, 360)):
        ctx.move_to(x - w / 2, feet - 120)
        ctx.line_to(x - w / 4, feet - 120 - h)
        ctx.line_to(x + w / 5, feet - 120 - h * 0.8)
        ctx.line_to(x + w / 2, feet - 120)
        ctx.close_path()
        ctx.set_source_rgb(0.85, 0.95, 1.0)
        ctx.fill_preserve()
        ctx.set_source_rgba(*INK, 0.3)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.rectangle(0, feet - 120, W, 120)
    ctx.set_source_rgb(0.35, 0.6, 0.85)
    ctx.fill()
    ground(ctx, feet, (0.93, 0.97, 1.0))
    falling(ctx, t, 30, (1, 1, 1), 60, 5)


def L_aurora(ctx, t, feet):
    bgc = (0.03, 0.06, 0.18)
    sky(ctx, bgc, (0.08, 0.15, 0.3), feet)
    stars(ctx, t, 60, feet - 300)
    for k, c in enumerate(((0.3, 1.0, 0.6), (0.4, 0.8, 1.0), (0.7, 0.4, 1.0))):
        ctx.move_to(0, 400 + k * 90)
        for x in range(0, W + 1, 20):
            ctx.line_to(x, 400 + k * 90 + 70 * math.sin(x / 160 + t * 0.8 + k))
        ctx.line_to(W, 700 + k * 90)
        ctx.line_to(0, 700 + k * 90)
        ctx.close_path()
        ctx.set_source_rgba(*c, 0.22)
        ctx.fill()
    hills(ctx, feet - 100, 60, 0.005, (0.12, 0.18, 0.3), 2)
    ground(ctx, feet, (0.85, 0.9, 0.97))


def L_ciudad(ctx, t, feet):
    sky(ctx, (0.55, 0.8, 1.0), (0.9, 0.96, 1.0), feet)
    clouds(ctx, t, 3, 200, 500)
    building_row(ctx, feet - 140, t, [(0.7, 0.75, 0.85), (0.8, 0.8, 0.85), (0.65, 0.7, 0.8)], 4, False, 400, 900)
    building_row(ctx, feet - 60, t, [(0.95, 0.75, 0.55), (0.75, 0.85, 0.95), (0.95, 0.85, 0.6)], 7, False, 200, 500)
    for k in range(3):  # coches al fondo
        x = (t * (160 + k * 60) + k * 400) % (W + 300) - 150
        y = feet - 40
        rect(ctx, x, y - 40, 120, 40, [(0.9, 0.3, 0.3), (0.3, 0.5, 0.9), (1, 0.8, 0.2)][k], 4)
        for wx in (20, 95):
            ctx.arc(x + wx, y, 14, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
    ground(ctx, feet, (0.6, 0.62, 0.66))


def L_noche(ctx, t, feet):
    bgc = (0.07, 0.08, 0.22)
    sky(ctx, bgc, (0.2, 0.18, 0.4), feet)
    stars(ctx, t, 50, 700)
    moon(ctx, 830, 330, 80, bgc)
    building_row(ctx, feet - 60, t, [(0.2, 0.22, 0.35), (0.25, 0.25, 0.4), (0.18, 0.2, 0.3)], 5, True, 350, 800)
    ground(ctx, feet, (0.3, 0.3, 0.38))


def L_espacio(ctx, t, feet):
    bgc = (0.03, 0.03, 0.12)
    sky(ctx, bgc, (0.1, 0.05, 0.25))
    stars(ctx, t, 130, H)
    for (x, y, r, c) in ((180, 420, 70, (0.95, 0.55, 0.3)), (900, 900, 45, (0.5, 0.7, 1.0))):
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgb(*c)
        ctx.fill()
    ph = (t * 0.4) % 1  # estrella fugaz
    sx, sy = -100 + ph * 1400, 200 + ph * 500
    g = cairo.LinearGradient(sx - 200, sy - 70, sx, sy)
    g.add_color_stop_rgba(0, 1, 1, 1, 0)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.9)
    ctx.move_to(sx - 200, sy - 70)
    ctx.line_to(sx, sy)
    ctx.set_source(g)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.save()  # "suelo" de asteroide
    ctx.rectangle(0, feet, W, H - feet)
    ctx.set_source_rgb(0.4, 0.38, 0.45)
    ctx.fill()
    ctx.restore()
    for k in range(5):
        ctx.save()
        ctx.translate(100 + k * 220, feet + 120 + 40 * (k % 2))
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, 60, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.3, 0.28, 0.35)
        ctx.fill()


def L_luna(ctx, t, feet):
    bgc = (0.02, 0.02, 0.08)
    sky(ctx, bgc, (0.06, 0.06, 0.15), feet)
    stars(ctx, t, 90, feet)
    ctx.arc(820, 380, 110, 0, 2 * math.pi)  # la Tierra
    ctx.set_source_rgb(0.3, 0.6, 1.0)
    ctx.fill()
    for (a, b, r) in ((790, 350, 40), (860, 410, 30)):
        ctx.arc(a, b, r, 0, 2 * math.pi)
        ctx.set_source_rgb(0.3, 0.78, 0.4)
        ctx.fill()
    hills(ctx, feet - 30, 25, 0.008, (0.7, 0.7, 0.72), 1)
    ground(ctx, feet, (0.75, 0.75, 0.77))
    for k in range(6):
        ctx.save()
        ctx.translate(80 + k * 190, feet + 100 + (k % 3) * 70)
        ctx.scale(1, 0.3)
        ctx.arc(0, 0, 50 + (k % 2) * 30, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.6, 0.6, 0.62)
        ctx.fill()


def L_marte(ctx, t, feet):
    sky(ctx, (0.95, 0.65, 0.45), (1.0, 0.82, 0.65), feet)
    ctx.arc(250, 330, 40, 0, 2 * math.pi)
    ctx.set_source_rgb(1, 0.95, 0.85)
    ctx.fill()
    hills(ctx, feet - 260, 90, 0.005, (0.8, 0.4, 0.25), 2)
    hills(ctx, feet - 120, 40, 0.008, (0.88, 0.48, 0.3), 5)
    ground(ctx, feet, (0.9, 0.5, 0.32))
    falling(ctx, t, 25, (0.95, 0.6, 0.4), 30, 4, wind=3.0)


def L_granja(ctx, t, feet):
    sky(ctx, (0.55, 0.82, 1.0), (0.9, 0.97, 1.0), feet)
    sun(ctx, 180, 320, 80, t)
    clouds(ctx, t, 3, 300, 600)
    hills(ctx, feet - 260, 50, 0.005, (0.6, 0.85, 0.45), 1)
    x0 = 700  # granero
    rect(ctx, x0, feet - 420, 300, 300, (0.85, 0.25, 0.22))
    ctx.move_to(x0 - 20, feet - 420)
    ctx.line_to(x0 + 150, feet - 560)
    ctx.line_to(x0 + 320, feet - 420)
    ctx.close_path()
    ctx.set_source_rgb(0.6, 0.18, 0.15)
    ctx.fill()
    rect(ctx, x0 + 100, feet - 280, 100, 160, (1, 1, 1))
    for k in range(12):  # valla
        rect(ctx, k * 95, feet - 120, 18, 120, (0.95, 0.9, 0.8), 3)
    rect(ctx, 0, feet - 95, W, 14, (0.95, 0.9, 0.8), 3)
    ground(ctx, feet, (0.5, 0.78, 0.35))


def L_sabana(ctx, t, feet):
    sky(ctx, (1.0, 0.6, 0.35), (1.0, 0.85, 0.55), feet)
    sun(ctx, 540, 650, 160, t, (1.0, 0.75, 0.3))
    hills(ctx, feet - 200, 30, 0.004, (0.85, 0.6, 0.3), 1, outline=False)
    for x, s in ((200, 1.1), (850, 0.85)):  # acacias
        ctx.move_to(x, feet - 150)
        ctx.line_to(x + 10 * s, feet - 380 * s - 150)
        ctx.set_source_rgb(0.3, 0.2, 0.12)
        ctx.set_line_width(26 * s)
        ctx.stroke()
        ctx.save()
        ctx.translate(x + 10 * s, feet - 400 * s - 150)
        ctx.scale(1, 0.3)
        ctx.arc(0, 0, 200 * s, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.3, 0.45, 0.2)
        ctx.fill()
    for k in range(40):  # hierba
        x = k * 28
        ctx.move_to(x, feet)
        ctx.line_to(x + 8 + 6 * math.sin(t * 2 + k), feet - 50 - (k % 3) * 15)
        ctx.set_source_rgb(0.75, 0.6, 0.25)
        ctx.set_line_width(6)
        ctx.stroke()
    ground(ctx, feet, (0.88, 0.7, 0.38))


def L_cueva(ctx, t, feet):
    sky(ctx, (0.18, 0.15, 0.17), (0.28, 0.23, 0.22))
    for k in range(9):  # estalactitas
        x = 40 + k * 125
        h = 160 + (k * 53) % 180
        ctx.move_to(x - 50, 0)
        ctx.line_to(x, h)
        ctx.line_to(x + 50, 0)
        ctx.close_path()
        ctx.set_source_rgb(0.32, 0.27, 0.27)
        ctx.fill()
    for x in (150, 930):  # antorchas con llama
        rect(ctx, x - 10, 700, 20, 110, (0.45, 0.3, 0.18), 4)
        f = 1 + 0.15 * math.sin(t * 17 + x)
        g = cairo.RadialGradient(x, 680, 10, x, 680, 260 * f)
        g.add_color_stop_rgba(0, 1, 0.8, 0.4, 0.45)
        g.add_color_stop_rgba(1, 1, 0.6, 0.2, 0)
        ctx.arc(x, 680, 260 * f, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        ctx.move_to(x, 640 - 30 * f)
        ctx.curve_to(x + 35, 680, x + 20, 705, x, 705)
        ctx.curve_to(x - 20, 705, x - 35, 680, x, 640 - 30 * f)
        ctx.set_source_rgb(1, 0.6, 0.15)
        ctx.fill()
    ground(ctx, feet, (0.36, 0.3, 0.28))


def L_volcanico(ctx, t, feet):
    sky(ctx, (0.35, 0.1, 0.1), (0.75, 0.3, 0.15), feet)
    rising(ctx, t, 30, (1.0, 0.6, 0.2), 70, 5, alpha=0.8)
    hills(ctx, feet - 220, 120, 0.004, (0.25, 0.15, 0.15), 3)
    ground(ctx, feet, (0.2, 0.13, 0.13))
    for k in range(3):  # ríos de lava
        y = feet + 90 + k * 150
        ctx.move_to(0, y)
        for x in range(0, W + 1, 30):
            ctx.line_to(x, y + 15 * math.sin(x / 80 + k))
        ctx.set_source_rgb(1.0, 0.45 + 0.1 * math.sin(t * 3 + k), 0.1)
        ctx.set_line_width(26)
        ctx.stroke()


def L_egipto(ctx, t, feet):
    sky(ctx, (0.55, 0.8, 1.0), (1.0, 0.92, 0.7), feet)
    sun(ctx, 870, 300, 85, t)
    for (x, h) in ((250, 520), (560, 680), (860, 420)):
        ctx.move_to(x - h * 0.8, feet - 120)
        ctx.line_to(x, feet - 120 - h)
        ctx.line_to(x + h * 0.8, feet - 120)
        ctx.close_path()
        ctx.set_source_rgb(0.92, 0.75, 0.45)
        ctx.fill_preserve()
        ctx.set_source_rgba(*INK, 0.35)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.move_to(x, feet - 120 - h)
        ctx.line_to(x + h * 0.8, feet - 120)
        ctx.line_to(x + h * 0.15, feet - 120)
        ctx.close_path()
        ctx.set_source_rgba(0, 0, 0, 0.12)
        ctx.fill()
    hills(ctx, feet - 80, 30, 0.006, (0.97, 0.82, 0.52), 1)
    ground(ctx, feet, (0.97, 0.84, 0.55))


def L_castillo(ctx, t, feet):
    sky(ctx, (0.6, 0.8, 1.0), (0.95, 0.95, 1.0), feet)
    clouds(ctx, t, 4, 200, 500)
    hills(ctx, feet - 330, 60, 0.004, (0.45, 0.7, 0.4), 2)
    c = (0.72, 0.72, 0.78)
    bx, by = 330, feet - 380
    rect(ctx, bx, by - 300, 420, 300, c)
    for tx in (bx - 60, bx + 420):
        rect(ctx, tx, by - 450, 100, 450, c)
        ctx.move_to(tx - 15, by - 450)
        ctx.line_to(tx + 50, by - 580)
        ctx.line_to(tx + 115, by - 450)
        ctx.close_path()
        ctx.set_source_rgb(0.4, 0.3, 0.6)
        ctx.fill()
        ctx.move_to(tx + 50, by - 580)  # bandera ondeando
        ctx.line_to(tx + 50, by - 660)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.move_to(tx + 50, by - 660)
        for k in range(6):
            ctx.line_to(tx + 50 + k * 14, by - 660 + 6 * math.sin(t * 6 + k))
        for k in range(5, -1, -1):
            ctx.line_to(tx + 50 + k * 14, by - 625 + 6 * math.sin(t * 6 + k))
        ctx.close_path()
        ctx.set_source_rgb(0.95, 0.3, 0.3)
        ctx.fill()
    for k in range(6):
        rect(ctx, bx + k * 75, by - 340, 45, 40, c, 4)
    ctx.move_to(bx + 160, by)
    ctx.arc(bx + 210, by - 110, 50, math.pi, 0)
    ctx.line_to(bx + 260, by)
    ctx.close_path()
    ctx.set_source_rgb(0.35, 0.25, 0.18)
    ctx.fill()
    ground(ctx, feet, (0.5, 0.78, 0.42))


def L_laboratorio(ctx, t, feet):
    sky(ctx, (0.88, 0.93, 0.95), (0.8, 0.88, 0.92), feet)
    for y in range(0, feet, 90):
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.set_line_width(3)
    ctx.stroke()
    for sy in (520, 820):  # estanterías con matraces burbujeando
        rect(ctx, 60, sy, 960, 20, (0.6, 0.6, 0.65))
        for k in range(6):
            x = 120 + k * 160
            c = [(0.4, 0.9, 0.5), (0.9, 0.4, 0.7), (0.4, 0.7, 1.0)][k % 3]
            ctx.move_to(x - 15, sy - 120)
            ctx.line_to(x - 15, sy - 70)
            ctx.line_to(x - 50, sy)
            ctx.line_to(x + 50, sy)
            ctx.line_to(x + 15, sy - 70)
            ctx.line_to(x + 15, sy - 120)
            ctx.close_path()
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(4)
            ctx.stroke()
            ctx.move_to(x - 38, sy - 20)
            ctx.line_to(x + 38, sy - 20)
            ctx.line_to(x + 50, sy - 2)
            ctx.line_to(x - 50, sy - 2)
            ctx.close_path()
            ctx.set_source_rgb(*c)
            ctx.fill()
            for b in range(3):
                ph = (t * 0.9 + b / 3 + k * 0.2) % 1
                ctx.arc(x + 8 * math.sin(b + k), sy - 30 - 120 * ph, 6, 0, 2 * math.pi)
                ctx.set_source_rgba(*c, 1 - ph)
                ctx.fill()
    ground(ctx, feet, (0.75, 0.8, 0.85))


def L_hospital(ctx, t, feet):
    sky(ctx, (0.85, 0.95, 0.95), (0.78, 0.9, 0.92), feet)
    rect(ctx, 600, 400, 400, 260, (0.15, 0.2, 0.25))  # monitor cardiaco
    ctx.save()
    ctx.rectangle(610, 410, 380, 240)
    ctx.clip()
    off = (t * 220) % 380
    ctx.move_to(610, 540)
    for x in range(0, 800, 4):
        xx = 610 + x - off
        ph = (x % 190) / 190
        y = 540 - (130 if 0.4 < ph < 0.44 else (-50 if 0.44 < ph < 0.48 else 0))
        ctx.line_to(xx, y)
    ctx.set_source_rgb(0.3, 1.0, 0.5)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()
    rect(ctx, 80, 420, 140, 140, (1, 1, 1))
    rect(ctx, 130, 440, 40, 100, (0.95, 0.25, 0.25), 0)
    rect(ctx, 100, 470, 100, 40, (0.95, 0.25, 0.25), 0)
    ground(ctx, feet, (0.7, 0.85, 0.85))


def L_clase(ctx, t, feet):
    sky(ctx, (1.0, 0.95, 0.82), (0.98, 0.9, 0.75), feet)
    rect(ctx, 90, 330, 900, 520, (0.2, 0.42, 0.32), 14)  # pizarra
    ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.set_line_width(6)
    _txt(ctx, "E = mc²", 200, 480, 80, (1, 1, 1))
    _txt(ctx, "2 + 2 = 4", 560, 640, 60, (1, 1, 1))
    ctx.arc(780, 470, 70, 0, 2 * math.pi)
    ctx.stroke()
    k = (t * 0.5) % 1  # tiza escribiendo
    ctx.move_to(200, 760)
    ctx.line_to(200 + 600 * k, 760 + 10 * math.sin(k * 30))
    ctx.stroke()
    ground(ctx, feet, (0.75, 0.55, 0.38))


def L_estadio(ctx, t, feet):
    sky(ctx, (0.3, 0.5, 0.85), (0.6, 0.75, 0.95), feet - 400)
    for x in (120, 960):  # focos
        rect(ctx, x - 8, 150, 16, 300, (0.6, 0.6, 0.65), 3)
        rect(ctx, x - 70, 110, 140, 60, (1, 1, 0.85), 4)
    rnd = random.Random(4)
    ctx.rectangle(0, 500, W, feet - 700)
    ctx.set_source_rgb(0.4, 0.4, 0.5)
    ctx.fill()
    for k in range(260):  # público animando
        x, y = rnd.uniform(0, W), rnd.uniform(520, feet - 220)
        jump = max(0, math.sin(t * 6 + x / 60)) * 10
        ctx.arc(x, y - jump, 11, 0, 2 * math.pi)
        ctx.set_source_rgb(*rnd.choice([(0.95, 0.3, 0.3), (1, 1, 1), (0.3, 0.5, 0.95), (1, 0.85, 0.2)]))
        ctx.fill()
    ctx.rectangle(0, feet - 200, W, H)
    ctx.set_source_rgb(0.3, 0.72, 0.35)
    ctx.fill()
    for k in range(0, W, 120):
        ctx.rectangle(k, feet - 200, 60, H)
        ctx.set_source_rgba(1, 1, 1, 0.06)
        ctx.fill()
    ctx.move_to(0, feet + 100)
    ctx.line_to(W, feet + 100)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(8)
    ctx.stroke()


def L_cielo(ctx, t, feet):
    sky(ctx, (0.45, 0.72, 1.0), (0.85, 0.94, 1.0))
    clouds(ctx, t, 6, 150, 1100, speed=40, seed=11)
    for k in range(3):  # pájaros lejanos
        x = (t * 90 + k * 300) % (W + 200) - 100
        y = 400 + k * 120 + 20 * math.sin(t * 2 + k)
        f = 15 * math.sin(t * 9 + k)
        ctx.move_to(x - 30, y - f)
        ctx.line_to(x, y)
        ctx.line_to(x + 30, y - f)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
    for k in range(7):  # suelo de nubes
        cloud(ctx, k * 180, feet + 60, 1.6)
    ctx.rectangle(0, feet + 80, W, H)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()


def L_tormenta(ctx, t, feet):
    flash = 1.0 if (t % 2.6) < 0.08 else 0.0
    sky(ctx, [0.25 + 0.6 * flash] * 2 + [0.33 + 0.6 * flash], (0.45, 0.48, 0.55), feet)
    clouds(ctx, t, 6, 100, 450, speed=30, color=(0.35, 0.37, 0.45), alpha=1.0)
    if flash:
        ctx.move_to(700, 350)
        for (dx, dy) in ((-60, 160), (40, 150), (-80, 200), (30, 180)):
            ctx.rel_line_to(dx, dy)
        ctx.set_source_rgb(1, 1, 0.6)
        ctx.set_line_width(12)
        ctx.stroke()
    falling(ctx, t, 90, (0.75, 0.82, 1.0), 900, 3, streak=True, wind=-0.2)
    hills(ctx, feet - 120, 40, 0.006, (0.3, 0.42, 0.35), 2)
    ground(ctx, feet, (0.35, 0.45, 0.38))


def L_lago(ctx, t, feet):
    sky(ctx, (0.6, 0.82, 1.0), (0.95, 0.97, 1.0), feet - 300)
    for (x, h) in ((200, 600), (650, 750), (1000, 500)):
        ctx.move_to(x - 400, feet - 300)
        ctx.line_to(x, feet - 300 - h)
        ctx.line_to(x + 400, feet - 300)
        ctx.close_path()
        ctx.set_source_rgb(0.5, 0.6, 0.75)
        ctx.fill()
    ctx.rectangle(0, feet - 300, W, 300)
    ctx.set_source_rgb(0.35, 0.65, 0.9)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.set_line_width(5)
    for k in range(6):
        y = feet - 270 + k * 45
        x = (t * 40 + k * 170) % (W + 200) - 100
        ctx.move_to(x, y)
        ctx.line_to(x + 120, y)
        ctx.stroke()
    for k in range(10):  # juncos
        x = k * 115 + 30
        ctx.move_to(x, feet)
        ctx.line_to(x + 8 * math.sin(t * 2 + k), feet - 130)
        ctx.set_source_rgb(0.35, 0.55, 0.25)
        ctx.set_line_width(8)
        ctx.stroke()
    ground(ctx, feet, (0.55, 0.75, 0.4))


def L_cocina(ctx, t, feet):
    sky(ctx, (1.0, 0.96, 0.9), (0.97, 0.92, 0.85), feet)
    for y in range(300, 900, 70):
        for x in range(0, W, 70):
            ctx.rectangle(x + 2, y + 2, 66, 66)
            ctx.set_source_rgba(0.6, 0.8, 0.9, 0.35 if (x // 70 + y // 70) % 2 else 0.15)
            ctx.fill()
    for k in range(4):  # armarios
        rect(ctx, 40 + k * 255, 120, 235, 170, (0.95, 0.75, 0.5))
    rect(ctx, 0, feet - 360, W, 40, (0.85, 0.85, 0.88))
    rect(ctx, 650, feet - 470, 220, 110, (0.4, 0.4, 0.45))  # olla con vapor
    rising(ctx, t, 12, (1, 1, 1), 60, 14, y_from=feet - 470, alpha=0.35)
    for k in range(4):
        rect(ctx, 40 + k * 255, feet - 320, 235, 320, (0.92, 0.7, 0.45))
    ground(ctx, feet, (0.82, 0.68, 0.52))


def L_dormitorio(ctx, t, feet):
    bgc = (0.18, 0.2, 0.4)
    sky(ctx, (0.35, 0.33, 0.6), (0.28, 0.26, 0.5), feet)
    rect(ctx, 650, 280, 330, 380, bgc, 14)  # ventana con luna
    ctx.save()
    ctx.rectangle(650, 280, 330, 380)
    ctx.clip()
    stars(ctx, t, 12, 700, 8)
    moon(ctx, 830, 420, 70, bgc)
    ctx.restore()
    rect(ctx, 812, 280, 8, 380, (0.9, 0.9, 0.95), 0)
    rect(ctx, 650, 465, 330, 8, (0.9, 0.9, 0.95), 0)
    for k in range(3):  # zzz flotando
        ph = (t * 0.4 + k / 3) % 1
        _txt(ctx, "z", 250 + 60 * k + 40 * ph, 700 - 300 * ph, 50 + 30 * k, (1, 1, 1), 1 - ph)
    ground(ctx, feet, (0.55, 0.42, 0.38))


def L_museo(ctx, t, feet):
    sky(ctx, (0.95, 0.92, 0.86), (0.9, 0.86, 0.78), feet)
    for x in (40, 960):
        rect(ctx, x, 150, 80, feet - 150, (0.98, 0.96, 0.92))
    for k, c in enumerate(((0.4, 0.6, 0.9), (0.95, 0.6, 0.3), (0.5, 0.8, 0.5))):
        x = 180 + k * 260
        rect(ctx, x, 380, 200, 260, (0.85, 0.65, 0.25), 10)
        rect(ctx, x + 20, 400, 160, 220, c, 3)
        g = cairo.RadialGradient(x + 100, 330, 10, x + 100, 330, 220)
        g.add_color_stop_rgba(0, 1, 1, 0.8, 0.35 + 0.05 * math.sin(t * 2))
        g.add_color_stop_rgba(1, 1, 1, 0.8, 0)
        ctx.arc(x + 100, 330, 220, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    ground(ctx, feet, (0.65, 0.45, 0.3))


def L_ruinas(ctx, t, feet):
    sky(ctx, (0.6, 0.8, 1.0), (1.0, 0.95, 0.85), feet)
    sun(ctx, 200, 300, 70, t)
    clouds(ctx, t, 2, 350, 550)
    rect(ctx, 100, feet - 760, 880, 70, (0.95, 0.92, 0.82))
    for k in range(5):
        h = 640 if k not in (3,) else 380
        x = 140 + k * 190
        rect(ctx, x, feet - 50 - h if k != 3 else feet - 50 - h, 70, h, (0.95, 0.92, 0.82))
        for j in range(3):
            ctx.move_to(x + 18 + j * 17, feet - 50 - h + 10)
            ctx.line_to(x + 18 + j * 17, feet - 60)
        ctx.set_source_rgba(*INK, 0.25)
        ctx.set_line_width(3)
        ctx.stroke()
    rect(ctx, 60, feet - 60, 960, 60, (0.92, 0.88, 0.78))
    ground(ctx, feet, (0.85, 0.8, 0.6))


def L_pirata(ctx, t, feet):
    sky(ctx, (1.0, 0.7, 0.5), (1.0, 0.9, 0.75), feet - 300)
    sun(ctx, 540, feet - 320, 120, t, (1.0, 0.65, 0.3))
    ctx.rectangle(0, feet - 300, W, 300)
    ctx.set_source_rgb(0.2, 0.45, 0.75)
    ctx.fill()
    bob = 10 * math.sin(t * 1.5)  # barco pirata al fondo
    ctx.save()
    ctx.translate(820, feet - 330 + bob)
    ctx.rotate(0.03 * math.sin(t * 1.5))
    ctx.move_to(-150, 0)
    ctx.line_to(150, 0)
    ctx.line_to(110, 60)
    ctx.line_to(-110, 60)
    ctx.close_path()
    ctx.set_source_rgb(0.4, 0.25, 0.15)
    ctx.fill()
    ctx.rectangle(-5, -260, 10, 260)
    ctx.fill()
    ctx.move_to(5, -250)
    ctx.curve_to(110 + 10 * math.sin(t * 3), -200, 110, -100, 5, -60)
    ctx.close_path()
    ctx.set_source_rgb(0.95, 0.92, 0.85)
    ctx.fill()
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.set_line_width(5)
    for k in range(5):
        y = feet - 260 + k * 50
        ctx.move_to(0, y)
        for x in range(0, W + 1, 20):
            ctx.line_to(x, y + 7 * math.sin(x / 45 + t * 2 + k))
        ctx.stroke()
    ground(ctx, feet, (0.6, 0.42, 0.25))  # cubierta de madera
    for x in range(0, W, 120):
        ctx.move_to(x, feet)
        ctx.line_to(x, H)
    ctx.set_source_rgba(*INK, 0.3)
    ctx.set_line_width(4)
    ctx.stroke()


def L_prehistoria(ctx, t, feet):
    sky(ctx, (1.0, 0.75, 0.5), (1.0, 0.92, 0.7), feet)
    sun(ctx, 820, 330, 90, t, (1.0, 0.8, 0.3))
    ctx.move_to(250, feet - 200)  # volcán al fondo
    ctx.line_to(420, feet - 620)
    ctx.line_to(520, feet - 620)
    ctx.line_to(700, feet - 200)
    ctx.close_path()
    ctx.set_source_rgb(0.5, 0.38, 0.3)
    ctx.fill()
    rising(ctx, t, 8, (0.6, 0.55, 0.55), 50, 30, y_from=feet - 620, alpha=0.35)
    hills(ctx, feet - 180, 40, 0.006, (0.45, 0.65, 0.3), 1)
    for x in (100, 980):  # helechos gigantes
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.45 + 0.05 * math.sin(t * 2 + k)
            ctx.move_to(x, feet)
            ctx.curve_to(x + math.cos(a) * 100, feet + math.sin(a) * 200,
                         x + math.cos(a) * 200, feet + math.sin(a) * 300, x + math.cos(a) * 260, feet + math.sin(a) * 260)
            ctx.set_source_rgb(0.25, 0.55, 0.25)
            ctx.set_line_width(22)
            ctx.stroke()
    ground(ctx, feet, (0.6, 0.5, 0.3))


def _txt(ctx, s, x, y, size, color, alpha=1.0):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ctx.move_to(x, y)
    ctx.set_source_rgba(*color, alpha)
    ctx.show_text(s)


LANDSCAPES = {name[2:]: fn for name, fn in list(globals().items()) if name.startswith("L_")}
DARK = {"abismo", "aurora", "noche", "espacio", "luna", "cueva", "volcanico", "dormitorio", "tormenta"}


def draw_landscape(ctx, name, t, feet):
    LANDSCAPES[name](ctx, t, feet)
