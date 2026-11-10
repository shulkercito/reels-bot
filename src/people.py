"""Personajes disfrazados (astronauta, faraón, momia, robot...) en el estilo de los monigotes."""
import math

import cairo

from src.creatures import INK, Creature, Human, beat, bones, ellipse, eye, heart_shape, outline, shade, smile

_HUMAN = Human()
SKIN = (0.98, 0.82, 0.68)


def _rrect(ctx, x0, y0, x1, y1, r):
    ctx.new_sub_path()
    ctx.arc(x1 - r, y0 + r, r, -math.pi / 2, 0)
    ctx.arc(x1 - r, y1 - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y1 - r, r, math.pi / 2, math.pi)
    ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()


def _line(ctx, pts, w, color, outline_w=14):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(w + outline_w)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*color)
    ctx.set_line_width(w)
    ctx.stroke()


def _poly(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


class Person(Creature):
    def __init__(self, **p):
        d = dict(skin=SKIN, shirt=(0.3, 0.5, 0.9), pants=(0.3, 0.35, 0.55), hat=None, hold=None, face="normal",
                 beard=None, hair=None, cape=None, extras=(), float_=False, wave=False, inside="human")
        d.update(p)
        self.p = d
        self.color = d["shirt"]
        self.float_ = d["float_"]

    def body(self, ctx, t):
        ctx.new_path()
        if self.p["face"] == "ghost":
            self._ghost_path(ctx, t)
            return
        ctx.arc(0, -580, 95, 0, 2 * math.pi)
        _rrect(ctx, -130, -470, 130, -150, 60)

    def _ghost_path(self, ctx, t):
        ctx.move_to(-170, -150)
        ctx.curve_to(-190, -500, -120, -700, 0, -700)
        ctx.curve_to(120, -700, 190, -500, 170, -150)
        for k in range(6):
            x = 170 - (k + 1) * 340 / 6
            ctx.line_to(x + 28, -110 + 25 * math.sin(t * 5 + k))
            ctx.line_to(x, -150)
        ctx.close_path()

    def draw(self, ctx, t):
        p = self.p
        if p["face"] == "ghost":
            self._ghost_path(ctx, t)
            ctx.set_source_rgba(0.97, 0.97, 1.0, 0.92)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(10)
            ctx.stroke()
            for sx in (-1, 1):
                ellipse(ctx, sx * 45, -540, 26, 38)
                ctx.set_source_rgb(*INK)
                ctx.fill()
            ellipse(ctx, 0, -450, 30, 40 + 10 * math.sin(t * 4))
            ctx.fill()
            return
        skin, shirt, pants = p["skin"], p["shirt"], p["pants"]
        sw = math.sin(t * 2.2)
        # capa por detrás
        if p["cape"]:
            fl = 25 * math.sin(t * 3)
            _poly(ctx, [(-120, -470), (120, -470), (190 + fl, -60), (-190 + fl * 0.5, -60)])
            outline(ctx, p["cape"])
        if "backpack" in p["extras"]:
            _rrect(ctx, 90, -460, 210, -200, 30)
            outline(ctx, (0.85, 0.85, 0.88))
        # piernas
        for sx in (-1, 1):
            _line(ctx, [(sx * 60, -170), (sx * 70, -10)], 46, pants)
            _rrect(ctx, sx * 70 - 40, -40, sx * 70 + 40, 0, 18)
            outline(ctx, p.get("shoes", (0.25, 0.2, 0.2)), 6)
        # brazos
        hand_l = (-185 - 20 * sw, -240)
        if p["wave"]:
            hand_l = (-200, -640 + 30 * math.sin(t * 8))
        if p["face"] == "zombie":
            hand_l = (-330, -400 + 10 * sw)
        _line(ctx, [(-125, -430), hand_l], 38, shirt if "sleeves" not in p["extras"] else skin)
        hand_r = (185 + 20 * sw, -240) if p["face"] != "zombie" else (-300, -440 - 10 * sw)
        _line(ctx, [(125, -430), hand_r], 38, shirt if "sleeves" not in p["extras"] else skin)
        for h in (hand_l, hand_r):
            ctx.arc(h[0], h[1], 26, 0, 2 * math.pi)
            outline(ctx, p.get("gloves", skin), 8)
        # torso
        _rrect(ctx, -130, -470, 130, -150, 60)
        outline(ctx, shirt)
        self._torso_details(ctx, t)
        # objeto en la mano
        if p["hold"]:
            self._hold(ctx, t, hand_l)
        # cabeza
        if p["face"] == "robot":
            _rrect(ctx, -105, -680, 105, -490, 30)
            outline(ctx, (0.75, 0.78, 0.85))
            _rrect(ctx, -75, -640, 75, -560, 18)
            outline(ctx, (0.12, 0.15, 0.25), 6)
            for sx in (-1, 1):
                h = 6 if ((t + 0.3) % 3) < 0.12 else 22
                ellipse(ctx, sx * 35, -600, 18, h)
                ctx.set_source_rgb(0.3, 0.95, 1.0)
                ctx.fill()
            ctx.move_to(0, -680)
            ctx.line_to(0, -740)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(8)
            ctx.stroke()
            ctx.arc(0, -755, 18, 0, 2 * math.pi)
            ctx.set_source_rgb(1.0, 0.3 + 0.5 * abs(math.sin(t * 4)), 0.3)
            ctx.fill()
        else:
            if p["hat"] == "nemes":  # el tocado del faraón va por detrás de la cara
                self._hat(ctx, t, "nemes")
            if p["hair"] and p["hair"][0] == "long":
                ellipse(ctx, 0, -560, 120, 140)
                outline(ctx, p["hair"][1])
            if p["face"] == "alien":
                ellipse(ctx, 0, -600, 110, 120)
                outline(ctx, skin)
            else:
                ctx.arc(0, -580, 95, 0, 2 * math.pi)
                outline(ctx, skin)
            self._face(ctx, t)
        if p["beard"]:
            ctx.move_to(-80, -560)
            ctx.curve_to(-90, -420, 90, -420, 80, -560)
            ctx.curve_to(40, -510, -40, -510, -80, -560)
            outline(ctx, p["beard"], 7)
            smile(ctx, 0, -530, 20)
        if p["hair"] and p["hair"][0] in ("messy", "bun", "wild", "short"):
            self._hair(ctx, t, *p["hair"])
        if p["hat"] == "nemes":
            ctx.rectangle(-97, -665, 194, 30)
            outline(ctx, (1.0, 0.8, 0.2), 6)
            ctx.arc(0, -668, 20, 0, 2 * math.pi)
            outline(ctx, (0.2, 0.35, 0.8), 5)
        elif p["hat"]:
            self._hat(ctx, t, p["hat"])

    def _face(self, ctx, t):
        p = self.p
        f = p["face"]
        if f == "alien":
            for sx in (-1, 1):
                ctx.save()
                ctx.translate(sx * 45, -610)
                ctx.rotate(sx * 0.4)
                ellipse(ctx, 0, 0, 30, 48)
                ctx.restore()
                ctx.set_source_rgb(*INK)
                ctx.fill()
                ctx.arc(sx * 40, -625, 9, 0, 2 * math.pi)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
                ctx.move_to(sx * 40, -710)
                ctx.line_to(sx * 75, -790 + 10 * math.sin(t * 4 + sx))
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(7)
                ctx.stroke()
                ctx.arc(sx * 75, -800 + 10 * math.sin(t * 4 + sx), 16, 0, 2 * math.pi)
                outline(ctx, (0.6, 1.0, 0.4), 5)
            smile(ctx, 0, -530, 18)
            return
        if f == "skull":
            for sx in (-1, 1):
                ctx.arc(sx * 35, -595, 24, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.fill()
            _poly(ctx, [(-8, -560), (8, -560), (0, -540)])
            ctx.fill()
            for k in range(5):
                ctx.rectangle(-40 + k * 17, -525, 12, 20)
            ctx.set_line_width(4)
            ctx.stroke()
            return
        if f == "mummy":
            ctx.save()
            ctx.arc(0, -580, 95, 0, 2 * math.pi)
            ctx.clip()
            for k in range(8):
                ctx.move_to(-110, -660 + k * 26)
                ctx.line_to(110, -650 + k * 26 + (k % 2) * 14)
            ctx.set_source_rgba(*INK, 0.35)
            ctx.set_line_width(4)
            ctx.stroke()
            ctx.restore()
            eye(ctx, 30, -595, 18, t, 0.7, look=(-0.4, 0))
            return
        if f == "ninja":
            ctx.save()
            ctx.arc(0, -580, 95, 0, 2 * math.pi)
            ctx.clip()
            ctx.rectangle(-110, -700, 220, 240)
            ctx.set_source_rgb(0.15, 0.15, 0.18)
            ctx.fill()
            ctx.rectangle(-110, -625, 220, 55)
            ctx.set_source_rgb(*SKIN)
            ctx.fill()
            ctx.restore()
            eye(ctx, -32, -598, 16, t, 0.2, look=(-0.4, 0))
            eye(ctx, 32, -598, 16, t, 0.2, look=(-0.4, 0))
            return
        eye(ctx, -35, -595, 18, t, 0.4 + len(str(p.get("shirt"))) % 3, look=(-0.4, 0))
        eye(ctx, 35, -595, 18, t, 0.4 + len(str(p.get("shirt"))) % 3, look=(-0.4, 0))
        if "glasses" in p["extras"]:
            for sx in (-1, 1):
                ctx.arc(sx * 35, -595, 30, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(6)
                ctx.stroke()
            ctx.move_to(-5, -595)
            ctx.line_to(5, -595)
            ctx.stroke()
        if "patch" in p["extras"]:
            ctx.arc(35, -595, 26, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.move_to(-90, -640)
            ctx.line_to(95, -560)
            ctx.set_line_width(6)
            ctx.stroke()
        if f == "zombie":
            ctx.move_to(-30, -530)
            ctx.line_to(30, -540)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(7)
            ctx.stroke()
            return
        if f == "vampire":
            smile(ctx, 0, -540, 26)
            for sx in (-1, 1):
                _poly(ctx, [(sx * 12, -548), (sx * 22, -520), (sx * 30, -548)])
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
            return
        if "mustache" in p["extras"]:
            for sx in (-1, 1):
                ellipse(ctx, sx * 25, -548, 28, 12)
                ctx.set_source_rgb(0.3, 0.2, 0.15)
                ctx.fill()
        if "pacifier" in p["extras"]:
            ctx.arc(0, -535, 22, 0, 2 * math.pi)
            outline(ctx, (0.5, 0.8, 1.0), 5)
            return
        if not p["beard"]:
            smile(ctx, 0, -540, 26, max(0, math.sin(t * 5)) * 0.5)

    def _hair(self, ctx, t, kind, color):
        if kind == "messy" or kind == "wild":
            n = 9 if kind == "messy" else 12
            for k in range(n):
                a = math.pi + (k + 0.5) * math.pi / n
                r = 95 if kind == "messy" else 105
                ctx.new_sub_path()
                ctx.arc(math.cos(a) * r, -590 + math.sin(a) * r, 34 + 6 * math.sin(t * 3 + k) * (kind == "wild"),
                        0, 2 * math.pi)
            outline(ctx, color, 7)
        elif kind == "bun":
            ctx.arc(0, -690, 45, 0, 2 * math.pi)
            outline(ctx, color)
            ctx.arc(0, -600, 97, math.pi * 1.05, math.pi * 1.95)
            ctx.set_source_rgb(*color)
            ctx.set_line_width(30)
            ctx.stroke()
        elif kind == "short":
            ctx.arc(0, -585, 97, math.pi * 1.0, math.pi * 2.0)
            ctx.close_path()
            ctx.save()
            ctx.clip()
            ctx.rectangle(-120, -700, 240, 70)
            ctx.set_source_rgb(*color)
            ctx.fill()
            ctx.restore()

    def _hat(self, ctx, t, hat):
        if hat == "helmet_space":
            ctx.arc(0, -585, 130, 0, 2 * math.pi)
            ctx.set_source_rgba(0.75, 0.9, 1.0, 0.35)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(10)
            ctx.stroke()
            ctx.arc(-50, -640, 30, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 1, 1, 0.6)
            ctx.fill()
        elif hat == "nemes":
            _poly(ctx, [(-100, -660), (100, -660), (150, -470), (95, -470), (85, -560), (-85, -560), (-95, -470), (-150, -470)])
            outline(ctx, (1.0, 0.8, 0.2))
            ctx.save()
            _poly(ctx, [(-100, -660), (100, -660), (150, -470), (-150, -470)])
            ctx.clip()
            for k in range(7):
                ctx.rectangle(-160, -650 + k * 28, 320, 12)
            ctx.set_source_rgb(0.2, 0.35, 0.8)
            ctx.fill()
            ctx.restore()
            ctx.arc(0, -665, 22, 0, 2 * math.pi)
            outline(ctx, (1.0, 0.8, 0.2), 6)
        elif hat == "knight":
            ctx.arc(0, -590, 108, math.pi, 2 * math.pi)
            ctx.line_to(108, -500)
            ctx.line_to(-108, -500)
            ctx.close_path()
            outline(ctx, (0.75, 0.77, 0.82))
            ctx.rectangle(-90, -610, 180, 18)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            for k in range(5):
                ctx.arc(-20 + k * 14, -740 - k * 12 + 8 * math.sin(t * 4 + k), 30, 0, 2 * math.pi)
            ctx.set_source_rgb(0.95, 0.25, 0.25)
            ctx.fill()
        elif hat == "tricorn":
            _poly(ctx, [(-150, -640), (0, -720), (150, -640), (90, -670), (0, -690), (-90, -670)])
            ctx.move_to(-150, -640)
            ctx.curve_to(-100, -790, 100, -790, 150, -640)
            ctx.close_path()
            outline(ctx, (0.15, 0.15, 0.18))
            ctx.arc(0, -720, 18, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
        elif hat == "viking":
            ctx.arc(0, -610, 100, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.7, 0.72, 0.75))
            for sx in (-1, 1):
                ctx.move_to(sx * 90, -640)
                ctx.curve_to(sx * 170, -660, sx * 190, -760, sx * 150, -820)
                ctx.curve_to(sx * 150, -740, sx * 120, -700, sx * 80, -680)
                ctx.close_path()
                outline(ctx, (0.98, 0.95, 0.85))
        elif hat == "crown":
            _poly(ctx, [(-80, -650), (-90, -760), (-45, -700), (0, -780), (45, -700), (90, -760), (80, -650)])
            outline(ctx, (1.0, 0.82, 0.2))
            for x in (-45, 0, 45):
                ctx.arc(x, -675, 11, 0, 2 * math.pi)
                ctx.set_source_rgb(0.9, 0.2, 0.3)
                ctx.fill()
        elif hat == "wizard":
            ctx.move_to(-140, -650)
            ctx.line_to(30 + 20 * math.sin(t * 2), -900)
            ctx.line_to(140, -650)
            ctx.close_path()
            outline(ctx, (0.4, 0.3, 0.75))
            ellipse(ctx, 0, -650, 160, 28)
            outline(ctx, (0.4, 0.3, 0.75))
            for (x, y) in ((-30, -720), (40, -780), (10, -680)):
                ctx.arc(x, y, 9, 0, 2 * math.pi)
                ctx.set_source_rgb(1, 0.9, 0.3)
                ctx.fill()
        elif hat == "cowboy":
            ellipse(ctx, 0, -660, 175, 32)
            outline(ctx, (0.6, 0.4, 0.22))
            _rrect(ctx, -85, -770, 85, -655, 30)
            outline(ctx, (0.6, 0.4, 0.22))
            ctx.rectangle(-85, -690, 170, 20)
            ctx.set_source_rgb(0.3, 0.2, 0.1)
            ctx.fill()
        elif hat == "safari":
            ellipse(ctx, 0, -655, 165, 30)
            outline(ctx, (0.85, 0.78, 0.55))
            ctx.arc(0, -660, 95, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.85, 0.78, 0.55))
        elif hat == "chef":
            _rrect(ctx, -75, -760, 75, -650, 10)
            outline(ctx, (1, 1, 1))
            for x in (-50, 0, 50):
                ctx.new_sub_path()
                ctx.arc(x, -770, 50, 0, 2 * math.pi)
            outline(ctx, (1, 1, 1))
        elif hat == "roman":
            ctx.arc(0, -600, 103, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.85, 0.7, 0.3))
            for k in range(9):
                ctx.rectangle(-60 + k * 14, -770 + 5 * math.sin(t * 5 + k), 12, 90)
            ctx.set_source_rgb(0.9, 0.2, 0.2)
            ctx.fill()
        elif hat == "fire":
            ctx.arc(0, -610, 105, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.9, 0.2, 0.15))
            ellipse(ctx, 20, -605, 150, 24)
            outline(ctx, (0.9, 0.2, 0.15))
        elif hat == "samurai":
            _poly(ctx, [(-150, -620), (0, -700), (150, -620), (110, -600), (-110, -600)])
            outline(ctx, (0.6, 0.15, 0.15))
            _poly(ctx, [(-30, -690), (0, -790), (30, -690)])
            outline(ctx, (1.0, 0.8, 0.2), 6)
        elif hat == "bicorne":  # Napoleón
            ctx.move_to(-170, -650)
            ctx.curve_to(-120, -800, 120, -800, 170, -650)
            ctx.curve_to(80, -690, -80, -690, -170, -650)
            outline(ctx, (0.15, 0.15, 0.18))
            ctx.arc(0, -720, 16, 0, 2 * math.pi)
            outline(ctx, (0.9, 0.2, 0.25), 5)
        elif hat == "top_hat":
            ellipse(ctx, 0, -660, 140, 24)
            outline(ctx, (0.15, 0.15, 0.18))
            _rrect(ctx, -80, -840, 80, -660, 10)
            outline(ctx, (0.15, 0.15, 0.18))
            ctx.rectangle(-80, -700, 160, 22)
            ctx.set_source_rgb(0.85, 0.2, 0.25)
            ctx.fill()
        elif hat == "cap":
            ctx.arc(0, -620, 100, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.9, 0.25, 0.25))
            ellipse(ctx, -110, -625, 80, 18)
            outline(ctx, (0.9, 0.25, 0.25), 7)
        elif hat == "turban":
            for k in range(3):
                ellipse(ctx, 0, -650 - k * 30, 110 - k * 15, 40)
                outline(ctx, (0.98, 0.95, 0.9), 7)
            ctx.arc(0, -660, 14, 0, 2 * math.pi)
            outline(ctx, (0.3, 0.6, 1.0), 4)
        elif hat == "laurel":
            for sx in (-1, 1):
                for k in range(5):
                    a = math.pi * (1.05 + 0.18 * k) if sx < 0 else math.pi * (1.95 - 0.18 * k)
                    ellipse(ctx, math.cos(a) * 100, -585 + math.sin(a) * 100, 22, 12)
                    outline(ctx, (0.4, 0.7, 0.3), 4)
        elif hat == "headband":
            ctx.rectangle(-97, -650, 194, 26)
            ctx.set_source_rgb(0.95, 0.25, 0.25)
            ctx.fill()

    def _torso_details(self, ctx, t):
        p = self.p
        ex = p["extras"]
        if "coat" in ex:
            ctx.move_to(0, -470)
            ctx.line_to(0, -150)
            ctx.move_to(-50, -470)
            ctx.line_to(0, -380)
            ctx.line_to(50, -470)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        if "stethoscope" in ex:
            ctx.move_to(-60, -470)
            ctx.curve_to(-70, -330, 70, -330, 60, -470)
            ctx.set_source_rgb(0.2, 0.2, 0.25)
            ctx.set_line_width(8)
            ctx.stroke()
            ctx.arc(0, -340, 18, 0, 2 * math.pi)
            outline(ctx, (0.8, 0.8, 0.85), 5)
        if "stripes" in ex:
            ctx.save()
            _rrect(ctx, -130, -470, 130, -150, 60)
            ctx.clip()
            for k in range(6):
                ctx.rectangle(-140, -460 + k * 55, 280, 24)
            ctx.set_source_rgb(0.95, 0.95, 0.95)
            ctx.fill()
            ctx.restore()
        if "collar" in ex:
            ctx.arc(0, -470, 110, 0.15, math.pi - 0.15)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(48)
            ctx.stroke_preserve()
            ctx.set_source_rgb(1.0, 0.8, 0.2)
            ctx.set_line_width(36)
            ctx.stroke()
        if "bandages" in ex:
            ctx.save()
            _rrect(ctx, -130, -470, 130, -150, 60)
            ctx.clip()
            for k in range(12):
                ctx.move_to(-140, -470 + k * 30)
                ctx.line_to(140, -455 + k * 30 + (k % 2) * 12)
            ctx.set_source_rgba(*INK, 0.3)
            ctx.set_line_width(4)
            ctx.stroke()
            ctx.restore()
        if "armor" in ex:
            ctx.arc(0, -330, 70, 0, 2 * math.pi)
            outline(ctx, (0.85, 0.87, 0.9), 7)
            _poly(ctx, [(0, -380), (30, -330), (0, -280), (-30, -330)])
            ctx.set_source_rgb(0.9, 0.25, 0.25)
            ctx.fill()
        if "number" in ex:
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(120)
            ctx.move_to(-40, -260)
            ctx.text_path("7")
            outline(ctx, (1, 1, 1), 6)
        if "emblem" in ex:
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                r = 60 if k % 2 == 0 else 26
                (ctx.move_to if k == 0 else ctx.line_to)(math.cos(a) * r, -330 + math.sin(a) * r)
            ctx.close_path()
            outline(ctx, (1.0, 0.85, 0.2), 6)
        if "fur" in ex:
            _poly(ctx, [(-130, -440), (60, -470), (130, -300), (110, -170), (-20, -220), (-130, -170)])
            outline(ctx, (0.6, 0.45, 0.25), 6)
            for (a, b) in ((-60, -350), (40, -300), (-10, -250)):
                ctx.arc(a, b, 14, 0, 2 * math.pi)
                ctx.set_source_rgb(0.35, 0.25, 0.15)
                ctx.fill()
        if "diaper" in ex:
            _rrect(ctx, -130, -260, 130, -150, 40)
            outline(ctx, (1, 1, 1))
        if "torn" in ex:
            for k in range(4):
                _poly(ctx, [(-100 + k * 60, -150), (-70 + k * 60, -200), (-40 + k * 60, -150)])
                ctx.set_source_rgb(*self.p["skin"])
                ctx.fill()
        if "medals" in ex:
            for k in range(3):
                ctx.move_to(-70 + k * 30, -440)
                ctx.line_to(-70 + k * 30, -400)
                ctx.set_source_rgb(*((0.9, 0.2, 0.25), (0.2, 0.4, 0.9), (0.9, 0.2, 0.25))[k])
                ctx.set_line_width(14)
                ctx.stroke()
                ctx.arc(-70 + k * 30, -390, 13, 0, 2 * math.pi)
                outline(ctx, (1, 0.8, 0.2), 4)
        if "tie" in ex:
            _poly(ctx, [(-15, -465), (15, -465), (25, -300), (0, -270), (-25, -300)])
            outline(ctx, (0.85, 0.2, 0.25), 5)
        if "toga" in ex:
            _poly(ctx, [(-130, -440), (-60, -470), (130, -200), (130, -150), (60, -150)])
            outline(ctx, (0.98, 0.97, 0.94), 6)
        if "suit_panel" in ex:
            _rrect(ctx, -60, -420, 60, -320, 14)
            outline(ctx, (0.3, 0.5, 0.9), 5)
            for k in range(3):
                ctx.arc(-30 + k * 30, -370, 9, 0, 2 * math.pi)
                ctx.set_source_rgb(*((1, 0.3, 0.3), (0.3, 1, 0.4), (1, 0.9, 0.3))[k])
                ctx.fill()

    def _hold(self, ctx, t, hand):
        x, y = hand
        h = self.p["hold"]
        if h == "sword":
            _line(ctx, [(x, y), (x - 40, y - 260)], 18, (0.85, 0.88, 0.92), 10)
            ctx.rectangle(x - 45, y - 20, 70, 16)
            outline(ctx, (0.6, 0.45, 0.2), 5)
        elif h == "club":
            ctx.move_to(x, y)
            ctx.line_to(x - 60, y - 200)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(56)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke_preserve()
            ctx.set_source_rgb(0.6, 0.42, 0.25)
            ctx.set_line_width(44)
            ctx.stroke()
        elif h == "wand":
            _line(ctx, [(x, y), (x - 60, y - 160)], 10, (0.45, 0.3, 0.2), 8)
            for k in range(5):
                ph = (t * 1.5 + k / 5) % 1
                ctx.arc(x - 60 + 40 * math.sin(k * 2) * ph, y - 160 - 80 * ph, 9 * (1 - ph) + 2, 0, 2 * math.pi)
                ctx.set_source_rgba(1, 0.9, 0.3, 1 - ph)
                ctx.fill()
        elif h == "flask":
            _poly(ctx, [(x - 15, y - 90), (x + 15, y - 90), (x + 15, y - 50), (x + 55, y + 20), (x - 55, y + 20), (x - 15, y - 50)])
            outline(ctx, (0.6, 1.0, 0.5), 6)
            for k in range(3):
                ph = (t + k / 3) % 1
                ctx.arc(x + 10 * math.sin(k), y - 100 - 120 * ph, 10, 0, 2 * math.pi)
                ctx.set_source_rgba(0.6, 1, 0.5, 1 - ph)
                ctx.fill()
        elif h == "shield":
            _poly(ctx, [(x - 80, y - 110), (x + 80, y - 110), (x + 70, y + 30), (x, y + 100), (x - 70, y + 30)])
            outline(ctx, (0.85, 0.2, 0.2))
            ctx.arc(x, y - 20, 30, 0, 2 * math.pi)
            outline(ctx, (1, 0.85, 0.2), 6)
        elif h == "ball":
            b = abs(math.sin(t * 4)) * 120
            ctx.arc(-260, -60 - b, 55, 0, 2 * math.pi)
            outline(ctx, (1, 1, 1), 8)
            _poly(ctx, [(-260, -85 - b), (-238, -68 - b), (-246, -42 - b), (-274, -42 - b), (-282, -68 - b)])
            ctx.set_source_rgb(*INK)
            ctx.fill()
        elif h == "torch":
            _line(ctx, [(x, y), (x - 20, y - 150)], 18, (0.5, 0.35, 0.2), 10)
            f = 1 + 0.15 * math.sin(t * 17)
            ctx.move_to(x - 20, y - 150 - 90 * f)
            ctx.curve_to(x + 30, y - 170, x + 20, y - 140, x - 20, y - 140)
            ctx.curve_to(x - 60, y - 140, x - 70, y - 170, x - 20, y - 150 - 90 * f)
            ctx.set_source_rgb(1, 0.6, 0.15)
            ctx.fill()
        elif h == "flag":
            _line(ctx, [(x, y + 40), (x, y - 300)], 10, (0.8, 0.8, 0.82), 8)
            ctx.move_to(x, y - 300)
            for k in range(7):
                ctx.line_to(x - k * 22, y - 300 + 8 * math.sin(t * 5 + k))
            for k in range(6, -1, -1):
                ctx.line_to(x - k * 22, y - 210 + 8 * math.sin(t * 5 + k))
            ctx.close_path()
            outline(ctx, (0.95, 0.3, 0.3), 6)
        elif h == "cane":
            _line(ctx, [(x, y), (x - 10, -5)], 14, (0.55, 0.35, 0.2), 8)
        elif h == "spoon":
            _line(ctx, [(x, y), (x - 50, y - 150)], 14, (0.8, 0.8, 0.85), 8)
            ellipse(ctx, x - 58, y - 175, 30, 40)
            outline(ctx, (0.8, 0.8, 0.85), 6)
        elif h == "binoculars":
            for dx in (-25, 25):
                _rrect(ctx, x + dx - 22, y - 70, x + dx + 22, y + 10, 10)
                outline(ctx, (0.25, 0.25, 0.3), 6)
        elif h == "katana":
            ctx.move_to(x, y)
            ctx.curve_to(x - 30, y - 120, x - 30, y - 220, x - 10, y - 320)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(20)
            ctx.stroke_preserve()
            ctx.set_source_rgb(0.9, 0.92, 0.95)
            ctx.set_line_width(10)
            ctx.stroke()
        elif h == "book":
            _rrect(ctx, x - 70, y - 60, x + 70, y + 40, 8)
            outline(ctx, (0.85, 0.3, 0.3), 7)
            ctx.move_to(x, y - 60)
            ctx.line_to(x, y + 40)
            ctx.set_line_width(5)
            ctx.stroke()
        elif h == "telescope":
            _line(ctx, [(x, y), (x - 160, y - 120)], 34, (0.35, 0.4, 0.75), 10)
        elif h == "spear":
            _line(ctx, [(x, y + 150), (x - 20, y - 300)], 12, (0.55, 0.38, 0.22), 8)
            _poly(ctx, [(x - 40, y - 290), (x - 20, y - 380), (x, y - 290)])
            outline(ctx, (0.85, 0.88, 0.92), 6)
        elif h == "bow":
            ctx.arc(x, y - 20, 150, math.pi * 0.6, math.pi * 1.4)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(20)
            ctx.stroke_preserve()
            ctx.set_source_rgb(0.6, 0.4, 0.22)
            ctx.set_line_width(10)
            ctx.stroke()
            ctx.move_to(x + 150 * math.cos(math.pi * 0.6), y - 20 + 150 * math.sin(math.pi * 0.6))
            ctx.line_to(x + 150 * math.cos(math.pi * 1.4), y - 20 + 150 * math.sin(math.pi * 1.4))
            ctx.set_source_rgb(0.9, 0.9, 0.9)
            ctx.set_line_width(3)
            ctx.stroke()
        elif h == "trident":
            _line(ctx, [(x, y + 150), (x, y - 280)], 12, (1.0, 0.8, 0.2), 8)
            for dx in (-40, 0, 40):
                _line(ctx, [(x + dx, y - 280), (x + dx, y - 360)], 10, (1.0, 0.8, 0.2), 6)
            _line(ctx, [(x - 40, y - 280), (x + 40, y - 280)], 10, (1.0, 0.8, 0.2), 6)
        elif h == "microphone":
            _line(ctx, [(x, y), (x - 30, y - 100)], 16, (0.25, 0.25, 0.3), 8)
            ctx.arc(x - 35, y - 125, 36, 0, 2 * math.pi)
            outline(ctx, (0.75, 0.75, 0.8), 6)
            for k in range(3):
                ph = (t * 1.5 + k / 3) % 1
                ctx.arc(x - 35, y - 125, 50 + 90 * ph, -2.6, -1.8)
                ctx.set_source_rgba(0.4, 0.8, 1, 1 - ph)
                ctx.set_line_width(5)
                ctx.stroke()
        elif h == "hose":
            ctx.move_to(x, y)
            ctx.line_to(x - 60, y - 40)
            ctx.set_source_rgb(0.3, 0.3, 0.3)
            ctx.set_line_width(24)
            ctx.stroke()
            for k in range(8):
                ph = (t * 2 + k / 8) % 1
                ctx.arc(x - 60 - 300 * ph, y - 40 - 120 * ph + 200 * ph * ph, 12, 0, 2 * math.pi)
                ctx.set_source_rgba(0.5, 0.75, 1, 1 - ph * 0.5)
                ctx.fill()

    def inside(self, ctx, t):
        kind = self.p["inside"]
        if kind == "robot":
            for (x, y, r, sp) in ((-40, -380, 55, 1), (50, -300, 40, -1.4), (-30, -230, 30, 2), (0, -590, 45, 1)):
                ctx.save()
                ctx.translate(x, y)
                ctx.rotate(t * sp)
                for k in range(8):
                    ctx.rotate(math.pi / 4)
                    ctx.rectangle(r * 0.8, -10, r * 0.4, 20)
                ctx.arc(0, 0, r * 0.85, 0, 2 * math.pi)
                ctx.restore()
                ctx.set_source_rgb(0.75, 0.8, 0.9)
                ctx.fill()
                ctx.arc(x, y, r * 0.3, 0, 2 * math.pi)
                ctx.set_source_rgb(0.1, 0.15, 0.3)
                ctx.fill()
            for k in range(4):
                ctx.rectangle(-100 + k * 50, -200, 30, 30)
                ctx.set_source_rgb(0.3, 1.0, 0.5) if (int(t * 3) + k) % 2 else ctx.set_source_rgb(0.2, 0.4, 0.3)
                ctx.fill()
        elif kind == "ghost":
            for k in range(6):
                ph = (t * 0.7 + k / 6) % 1
                ctx.arc(30 * math.sin(k * 2), -200 - 450 * ph, 14, 0, 2 * math.pi)
                ctx.set_source_rgba(0.6, 1, 1, 1 - ph)
                ctx.fill()
        elif kind == "skeleton":
            bones(ctx, 0, -470, 0, -160, 16)
            for k in range(5):
                ctx.move_to(0, -440 + k * 40)
                ctx.curve_to(-80, -450 + k * 40, -110, -420 + k * 40, -100, -400 + k * 40)
                ctx.move_to(0, -440 + k * 40)
                ctx.curve_to(80, -450 + k * 40, 110, -420 + k * 40, 100, -400 + k * 40)
            ctx.set_source_rgb(0.95, 0.97, 1)
            ctx.set_line_width(8)
            ctx.stroke()
        else:
            _HUMAN.inside(ctx, t)


SKIN2 = (0.78, 0.58, 0.42)
PEOPLE = {
    "astronaut": Person(shirt=(0.95, 0.95, 0.97), pants=(0.92, 0.92, 0.95), hat="helmet_space", gloves=(0.9, 0.9, 0.92),
                        extras=("backpack", "suit_panel"), hold="flag", float_=False),
    "pharaoh": Person(skin=SKIN2, shirt=(1.0, 0.97, 0.9), pants=(1.0, 0.95, 0.85), hat="nemes", extras=("collar", "sleeves"),
                      hold="cane"),
    "mummy": Person(skin=(0.95, 0.92, 0.8), shirt=(0.95, 0.92, 0.8), pants=(0.93, 0.9, 0.78), face="mummy",
                    extras=("bandages",), gloves=(0.95, 0.92, 0.8)),
    "knight": Person(shirt=(0.75, 0.77, 0.82), pants=(0.7, 0.72, 0.78), hat="knight", extras=("armor",), hold="sword",
                     gloves=(0.75, 0.77, 0.82)),
    "pirate": Person(shirt=(0.9, 0.25, 0.25), pants=(0.25, 0.25, 0.35), hat="tricorn", extras=("stripes", "patch"),
                     beard=(0.25, 0.18, 0.12), hold="sword"),
    "viking": Person(shirt=(0.55, 0.4, 0.3), pants=(0.4, 0.3, 0.25), hat="viking", beard=(0.95, 0.55, 0.2),
                     extras=("fur",), hold="shield"),
    "scientist": Person(shirt=(0.97, 0.97, 0.97), pants=(0.35, 0.4, 0.5), hair=("wild", (0.9, 0.9, 0.92)),
                        extras=("coat", "glasses"), hold="flask"),
    "doctor": Person(shirt=(0.97, 0.97, 0.97), pants=(0.4, 0.75, 0.75), hair=("short", (0.3, 0.2, 0.15)),
                     extras=("coat", "stethoscope")),
    "king": Person(shirt=(0.75, 0.15, 0.25), pants=(0.4, 0.2, 0.5), hat="crown", cape=(0.85, 0.2, 0.25),
                   beard=(0.55, 0.38, 0.25), hold="cane"),
    "queen": Person(shirt=(0.55, 0.3, 0.85), pants=(0.55, 0.3, 0.85), hat="crown", hair=("long", (0.95, 0.8, 0.35)),
                    cape=(0.4, 0.2, 0.7), wave=True),
    "robot": Person(shirt=(0.7, 0.74, 0.82), pants=(0.6, 0.64, 0.72), face="robot", gloves=(0.6, 0.64, 0.72),
                    extras=("suit_panel",), inside="robot", wave=True),
    "alien": Person(skin=(0.55, 0.9, 0.45), shirt=(0.75, 0.78, 0.85), pants=(0.7, 0.72, 0.8), face="alien",
                    gloves=(0.55, 0.9, 0.45), wave=True),
    "ghost": Person(face="ghost", float_=True, inside="ghost"),
    "skeleton": Person(skin=(0.96, 0.96, 0.92), shirt=(0.2, 0.2, 0.25), pants=(0.2, 0.2, 0.25), face="skull",
                       gloves=(0.96, 0.96, 0.92), inside="skeleton", wave=True),
    "caveman": Person(skin=SKIN2, shirt=SKIN2, pants=SKIN2, hair=("messy", (0.3, 0.2, 0.12)), beard=(0.3, 0.2, 0.12),
                      extras=("fur", "sleeves"), hold="club"),
    "chef": Person(shirt=(1, 1, 1), pants=(0.25, 0.25, 0.3), hat="chef", extras=("coat", "mustache"), hold="spoon"),
    "footballer": Person(shirt=(0.95, 0.95, 0.95), pants=(0.25, 0.3, 0.6), hair=("short", (0.2, 0.15, 0.1)),
                         extras=("number", "sleeves"), hold="ball"),
    "roman": Person(shirt=(0.85, 0.2, 0.2), pants=SKIN, hat="roman", extras=("armor",), hold="shield"),
    "samurai": Person(shirt=(0.6, 0.15, 0.15), pants=(0.2, 0.2, 0.25), hat="samurai", extras=("armor",), hold="katana"),
    "ninja": Person(shirt=(0.15, 0.15, 0.18), pants=(0.15, 0.15, 0.18), face="ninja", gloves=(0.15, 0.15, 0.18),
                    hat="headband", hold="katana"),
    "wizard": Person(shirt=(0.4, 0.3, 0.75), pants=(0.4, 0.3, 0.75), hat="wizard", beard=(0.95, 0.95, 0.97), hold="wand"),
    "cowboy": Person(shirt=(0.85, 0.35, 0.3), pants=(0.3, 0.4, 0.65), hat="cowboy", extras=("mustache",)),
    "explorer": Person(shirt=(0.8, 0.72, 0.5), pants=(0.7, 0.62, 0.42), hat="safari", hold="binoculars", extras=("sleeves",)),
    "baby": Person(shirt=(0.6, 0.85, 1.0), pants=SKIN, extras=("diaper", "pacifier"), hair=("short", (0.95, 0.85, 0.5))),
    "grandpa": Person(shirt=(0.6, 0.5, 0.75), pants=(0.45, 0.4, 0.4), extras=("glasses", "mustache"), hold="cane",
                      hair=("short", (0.9, 0.9, 0.92))),
    "firefighter": Person(shirt=(0.95, 0.8, 0.2), pants=(0.3, 0.3, 0.32), hat="fire", hold="hose"),
    "superhero": Person(shirt=(0.25, 0.45, 0.95), pants=(0.9, 0.2, 0.25), cape=(0.9, 0.2, 0.25), extras=("emblem",),
                        hair=("short", (0.2, 0.15, 0.1)), wave=True),
    "zombie": Person(skin=(0.6, 0.8, 0.5), shirt=(0.45, 0.5, 0.6), pants=(0.4, 0.35, 0.3), face="zombie", extras=("torn",)),
    "vampire": Person(skin=(0.92, 0.92, 0.95), shirt=(0.15, 0.15, 0.18), pants=(0.15, 0.15, 0.18), face="vampire",
                      cape=(0.6, 0.1, 0.15), hair=("short", (0.1, 0.1, 0.12))),
    "student": Person(shirt=(0.35, 0.75, 0.45), pants=(0.3, 0.35, 0.55), extras=("backpack", "glasses"),
                      hair=("short", (0.4, 0.25, 0.15))),
    "athlete": Person(shirt=(0.95, 0.35, 0.3), pants=(0.2, 0.2, 0.25), hat="headband", extras=("sleeves", "number")),
    "woman": Person(shirt=(0.95, 0.5, 0.65), pants=(0.3, 0.35, 0.6), hair=("long", (0.45, 0.28, 0.15)), wave=True),
}

PEOPLE_PARTS = {k: {"brain": (0, -590), "heart": (18, -345), "lungs": (-62, -370), "stomach": (30, -255),
                    "body": (0, -350), "head": (0, -580)} for k in PEOPLE}
