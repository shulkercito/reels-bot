"""Pack "GTA": personajes, vehículos, objetos y paisajes del universo de crimen urbano en Florida.

Todo es GENÉRICO y dibujado en el estilo de los monigotes: ni personajes, ni logos, ni diseños oficiales
de Rockstar Games. Sirve para que los vídeos del Especial GTA (y cualquier historia de crimen, policías,
atracos o Miami) se vean concretos.
"""
import math
import random

import cairo

from src import people, scenery
from src.creatures import INK, Creature, beat, ellipse, eye, flow_line, heart_shape, outline, shade, smile
from src.people import SKIN, Person, _line, _poly, _rrect
from src.things import face, gear, glow, poly, rrect

TAN = (0.85, 0.65, 0.48)
DARK_SKIN = (0.55, 0.38, 0.25)
GOLD = (1.0, 0.8, 0.2)
NEON_PINK = (1.0, 0.3, 0.75)
NEON_CYAN = (0.3, 0.95, 1.0)


# ============================================================ PERSONAJES
class GTAPerson(Person):
    """Persona con accesorios extra de calle: gafas de sol, cadena de oro, pasamontañas, placa..."""

    def _face(self, ctx, t):
        p = self.p
        if p["face"] == "masked":  # pasamontañas
            ctx.save()
            ctx.arc(0, -580, 95, 0, 2 * math.pi)
            ctx.clip()
            ctx.rectangle(-110, -700, 220, 260)
            ctx.set_source_rgb(0.15, 0.15, 0.18)
            ctx.fill()
            ellipse(ctx, 0, -598, 75, 30)
            ctx.set_source_rgb(*p["skin"])
            ctx.fill()
            ellipse(ctx, 0, -535, 26, 18)
            ctx.fill()
            ctx.restore()
            eye(ctx, -32, -598, 16, t, 0.3, look=(-0.4, 0))
            eye(ctx, 32, -598, 16, t, 0.3, look=(-0.4, 0))
            return
        super()._face(ctx, t)
        if "sunglasses" in p["extras"]:
            for sx in (-1, 1):
                _rrect(ctx, sx * 35 - 32, -615, sx * 35 + 32, -578, 14)
                ctx.set_source_rgb(0.08, 0.08, 0.12)
                ctx.fill()
                ctx.move_to(sx * 35 - 20, -608)
                ctx.line_to(sx * 35 - 5, -590)
                ctx.set_source_rgba(1, 1, 1, 0.5)
                ctx.set_line_width(5)
                ctx.stroke()
            ctx.move_to(-3, -600)
            ctx.line_to(3, -600)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6)
            ctx.stroke()
        if "scar" in p["extras"]:
            ctx.move_to(40, -640)
            ctx.line_to(60, -560)
            ctx.set_source_rgb(0.75, 0.3, 0.3)
            ctx.set_line_width(5)
            ctx.stroke()

    def _hat(self, ctx, t, hat):
        if hat == "police_cap":
            _rrect(ctx, -100, -720, 100, -640, 20)
            outline(ctx, (0.12, 0.18, 0.4))
            ellipse(ctx, -60, -640, 95, 18)
            outline(ctx, (0.08, 0.08, 0.12), 6)
            _poly(ctx, [(0, -715), (16, -690), (0, -665), (-16, -690)])
            outline(ctx, GOLD, 4)
        elif hat == "swat":
            ctx.arc(0, -600, 108, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.18, 0.2, 0.22))
            _rrect(ctx, -95, -620, 95, -585, 12)
            ctx.set_source_rgba(0.3, 0.5, 0.7, 0.8)
            ctx.fill()
        elif hat == "headphones":
            ctx.arc(0, -600, 112, math.pi * 1.05, math.pi * 1.95)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(26)
            ctx.stroke_preserve()
            ctx.set_source_rgb(0.95, 0.3, 0.4)
            ctx.set_line_width(14)
            ctx.stroke()
            for sx in (-1, 1):
                _rrect(ctx, sx * 108 - 26, -640, sx * 108 + 26, -555, 20)
                outline(ctx, (0.95, 0.3, 0.4), 7)
        elif hat == "hood":
            ctx.arc(0, -595, 125, math.pi * 0.85, math.pi * 2.15)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(48)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*self.p["shirt"])
            ctx.set_line_width(34)
            ctx.stroke()
        elif hat == "biker":
            ctx.arc(0, -595, 112, math.pi * 0.95, math.pi * 2.05)
            ctx.close_path()
            outline(ctx, (0.15, 0.15, 0.18))
            ctx.arc(-20, -650, 22, 0, 2 * math.pi)
            outline(ctx, (0.95, 0.85, 0.2), 5)
        elif hat == "beanie":
            ctx.arc(0, -615, 100, math.pi, 2 * math.pi)
            ctx.close_path()
            outline(ctx, (0.2, 0.25, 0.3))
            ctx.rectangle(-100, -635, 200, 30)
            outline(ctx, (0.25, 0.3, 0.35), 6)
        elif hat == "bandana":
            ctx.arc(0, -605, 98, math.pi * 1.0, math.pi * 2.0)
            ctx.close_path()
            outline(ctx, (0.85, 0.15, 0.2))
            for k in range(5):
                ctx.arc(-60 + k * 30, -650, 5, 0, 2 * math.pi)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()
        elif hat == "visor":
            ellipse(ctx, -60, -640, 110, 20)
            outline(ctx, (1.0, 1.0, 1.0), 6)
            ctx.rectangle(-97, -665, 194, 26)
            outline(ctx, (1.0, 1.0, 1.0), 6)
        else:
            super()._hat(ctx, t, hat)

    def _torso_details(self, ctx, t):
        super()._torso_details(ctx, t)
        ex = self.p["extras"]
        if "hawaiian" in ex:
            ctx.save()
            _rrect(ctx, -130, -470, 130, -150, 60)
            ctx.clip()
            rnd = random.Random(4)
            for k in range(14):
                x, y = rnd.uniform(-120, 120), rnd.uniform(-460, -160)
                for j in range(5):
                    a = j * 2 * math.pi / 5
                    ctx.new_sub_path()
                    ctx.arc(x + math.cos(a) * 14, y + math.sin(a) * 14, 10, 0, 2 * math.pi)
                ctx.set_source_rgb(*((1, 0.95, 0.4), (1, 0.5, 0.6), (1, 1, 1))[k % 3])
                ctx.fill()
            ctx.restore()
        if "tank_top" in ex:  # escote de camiseta de tirantes
            ctx.move_to(-70, -468)
            ctx.curve_to(-60, -400, 60, -400, 70, -468)
            ctx.close_path()
            ctx.set_source_rgb(*self.p["skin"])
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(5)
            ctx.stroke()
        if "gold_chain" in ex:
            ctx.arc(0, -470, 75, 0.35, math.pi - 0.35)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(20)
            ctx.stroke_preserve()
            ctx.set_source_rgb(*GOLD)
            ctx.set_line_width(12)
            ctx.stroke()
            ctx.arc(0, -400, 22, 0, 2 * math.pi)
            outline(ctx, GOLD, 5)
        if "badge" in ex:
            for k in range(10):
                a = -math.pi / 2 + k * math.pi / 5
                r = 34 if k % 2 == 0 else 16
                (ctx.move_to if k == 0 else ctx.line_to)(-60 + math.cos(a) * r, -390 + math.sin(a) * r)
            ctx.close_path()
            outline(ctx, GOLD, 5)
        if "vest" in ex:
            _rrect(ctx, -115, -455, 115, -185, 40)
            outline(ctx, (0.2, 0.22, 0.25), 7)
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(56)
            e = ctx.text_extents(self.p.get("vest_text", "POLICE"))
            ctx.move_to(-e.width / 2 - e.x_bearing, -310)
            ctx.set_source_rgb(1, 1, 1)
            ctx.show_text(self.p.get("vest_text", "POLICE"))
        if "jacket" in ex:
            for sx in (-1, 1):
                _poly(ctx, [(sx * 20, -470), (sx * 130, -470), (sx * 130, -150), (sx * 40, -150)])
                outline(ctx, (0.18, 0.15, 0.15), 6)
        if "tattoos" in ex:
            for (x, y) in ((-160, -350), (165, -330)):
                ctx.arc(x, y, 12, 0, 2 * math.pi)
                ctx.set_source_rgb(0.2, 0.3, 0.5)
                ctx.fill()

    def _hold(self, ctx, t, hand):
        x, y = hand
        h = self.p["hold"]
        if h == "money_bag":
            ctx.move_to(x - 20, y)
            ctx.curve_to(x - 110, y + 30, x - 100, y + 170, x, y + 170)
            ctx.curve_to(x + 100, y + 170, x + 110, y + 30, x + 20, y)
            ctx.close_path()
            outline(ctx, (0.85, 0.7, 0.45), 7)
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(80)
            ctx.move_to(x - 25, y + 130)
            ctx.set_source_rgb(0.3, 0.6, 0.3)
            ctx.show_text("$")
        elif h == "cash":
            for k in range(3):
                ctx.save()
                ctx.translate(x - 30 + k * 12, y - 20 - k * 8)
                ctx.rotate(-0.3 + 0.1 * math.sin(t * 4 + k))
                ctx.rectangle(-60, -30, 120, 60)
                ctx.restore()
                outline(ctx, (0.55, 0.85, 0.5), 5)
        elif h == "phone":
            _rrect(ctx, x - 30, y - 120, x + 30, y - 10, 10)
            outline(ctx, (0.15, 0.15, 0.2), 6)
            ctx.rectangle(x - 22, y - 110, 44, 85)
            ctx.set_source_rgb(0.4, 0.75, 1)
            ctx.fill()
        elif h == "controller":
            ellipse(ctx, x - 20, y - 30, 80, 45)
            outline(ctx, (0.2, 0.2, 0.25), 7)
            for k, c in enumerate(((1, 0.3, 0.3), (0.3, 0.8, 0.4), (0.3, 0.5, 1), (1, 0.85, 0.2))):
                ctx.arc(x + 15 + (k % 2) * 20, y - 45 + (k // 2) * 22, 8, 0, 2 * math.pi)
                ctx.set_source_rgb(*c)
                ctx.fill()
        elif h == "laptop":
            _poly(ctx, [(x - 90, y), (x + 90, y), (x + 70, y - 120), (x - 70, y - 120)])
            outline(ctx, (0.3, 0.32, 0.38), 6)
            rnd = random.Random(int(t * 5))
            for k in range(4):
                ctx.rectangle(x - 55, y - 105 + k * 22, rnd.uniform(30, 100), 10)
                ctx.set_source_rgb(0.3, 1, 0.5)
                ctx.fill()
        elif h == "handcuffs":
            for dx in (-35, 35):
                ctx.arc(x + dx, y - 30, 30, 0, 2 * math.pi)
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(16)
                ctx.stroke_preserve()
                ctx.set_source_rgb(0.8, 0.82, 0.86)
                ctx.set_line_width(8)
                ctx.stroke()
        elif h == "megaphone":
            _poly(ctx, [(x, y - 40), (x - 140, y - 100), (x - 140, y + 30), (x, y - 10)])
            outline(ctx, (1, 1, 1), 7)
            for k in range(3):
                ph = (t * 1.5 + k / 3) % 1
                ctx.arc(x - 150, y - 35, 40 + ph * 120, math.pi * 0.75, math.pi * 1.25)
                ctx.set_source_rgba(1, 0.9, 0.3, 1 - ph)
                ctx.set_line_width(6)
                ctx.stroke()
        elif h == "keys":
            ctx.arc(x, y - 20, 20, 0, 2 * math.pi)
            outline(ctx, (0.8, 0.82, 0.86), 6)
            _line(ctx, [(x, y), (x - 10, y + 70)], 10, GOLD, 6)
        else:
            super()._hold(ctx, t, hand)


P = GTAPerson
GTA_PEOPLE = {
    "gangster": P(skin=TAN, shirt=(1, 1, 1), pants=(0.25, 0.3, 0.5), extras=("tank_top", "gold_chain", "sunglasses", "tattoos"),
                  hat="bandana", hold="cash"),
    "cop": P(shirt=(0.15, 0.22, 0.45), pants=(0.12, 0.15, 0.3), hat="police_cap", extras=("badge", "sunglasses"),
             hold="handcuffs"),
    "swat": P(shirt=(0.2, 0.22, 0.25), pants=(0.2, 0.22, 0.25), hat="swat", extras=("vest",), gloves=(0.15, 0.15, 0.18),
              hold="megaphone"),
    "robber": P(shirt=(0.15, 0.15, 0.18), pants=(0.2, 0.2, 0.25), face="masked", gloves=(0.15, 0.15, 0.18),
                hold="money_bag", extras=("stripes",)),
    "heist_woman": P(skin=TAN, shirt=(0.2, 0.2, 0.25), pants=(0.25, 0.3, 0.5), hair=("long", (0.15, 0.1, 0.08)),
                     extras=("jacket", "sunglasses", "gold_chain"), hold="phone"),
    "florida_man": P(skin=(0.98, 0.72, 0.6), shirt=(0.2, 0.7, 0.85), pants=(0.95, 0.9, 0.75),
                     extras=("hawaiian", "sunglasses", "mustache"), hat="visor", wave=True),
    "biker": P(shirt=(0.2, 0.18, 0.18), pants=(0.25, 0.3, 0.45), hat="biker", beard=(0.45, 0.32, 0.2),
               extras=("jacket", "tattoos", "sunglasses"), hold="keys"),
    "hacker": P(shirt=(0.25, 0.28, 0.35), pants=(0.2, 0.2, 0.25), hat="hood", extras=("glasses",), hold="laptop"),
    "streamer": P(shirt=(0.6, 0.3, 0.9), pants=(0.2, 0.2, 0.25), hat="headphones", hair=("short", (0.2, 0.15, 0.1)),
                  hold="controller"),
    "game_dev": P(shirt=(0.3, 0.32, 0.38), pants=(0.3, 0.35, 0.55), hat="beanie", beard=(0.35, 0.25, 0.15),
                  extras=("glasses",), hold="laptop"),
    "businessman": P(shirt=(0.15, 0.15, 0.2), pants=(0.15, 0.15, 0.2), extras=("tie", "sunglasses"),
                     hair=("short", (0.3, 0.25, 0.2)), hold="phone"),
    "rapper": P(skin=DARK_SKIN, shirt=(0.95, 0.85, 0.2), pants=(0.15, 0.15, 0.2), extras=("gold_chain", "sunglasses"),
                hat="cap", hold="cash"),
    "beach_girl": P(skin=TAN, shirt=(1.0, 0.45, 0.6), pants=(0.4, 0.75, 0.95), hair=("long", (0.95, 0.8, 0.4)),
                    extras=("sunglasses", "tank_top"), wave=True),
    "detective": P(shirt=(0.6, 0.5, 0.35), pants=(0.35, 0.3, 0.25), hat="cowboy", extras=("coat", "badge"),
                   hold="phone"),
}
for _p in GTA_PEOPLE.values():
    _p.p.setdefault("vest_text", "POLICE")


# ============================================================ VEHÍCULOS Y OBJETOS
def _wheel(ctx, x, y, r, t, spin=8):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-t * spin)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    outline(ctx, (0.15, 0.15, 0.17))
    ctx.arc(0, 0, r * 0.5, 0, 2 * math.pi)
    outline(ctx, (0.8, 0.82, 0.86), 6)
    for k in range(5):
        ctx.rotate(2 * math.pi / 5)
        ctx.move_to(0, 0)
        ctx.line_to(r * 0.5, 0)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def _speed_lines(ctx, t, x0, y0, n=4):
    for k in range(n):
        ph = (t * 2.5 + k / n) % 1
        y = y0 + k * 35
        ctx.move_to(x0 + ph * 200, y)
        ctx.line_to(x0 + ph * 200 + 120, y)
        ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - ph))
        ctx.set_line_width(8)
        ctx.stroke()


class SportsCar(Creature):
    def __init__(self, color=(1.0, 0.3, 0.6), police=False, taxi=False):
        self.color, self.police, self.taxi = color, police, taxi

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-330, -110)
        ctx.line_to(-320, -190)
        ctx.curve_to(-250, -210, -150, -230, -100, -230)
        ctx.curve_to(-40, -320, 120, -320, 180, -230)
        ctx.curve_to(260, -225, 320, -210, 330, -180)
        ctx.line_to(330, -110)
        ctx.close_path()

    def draw(self, ctx, t):
        bounce = 4 * math.sin(t * 9)
        ctx.save()
        ctx.translate(0, bounce)
        _speed_lines(ctx, t, 330, -230)
        self.body(ctx, t)
        outline(ctx, self.color)
        if self.police:
            ctx.save()
            self.body(ctx, t)
            ctx.clip()
            ctx.rectangle(-140, -320, 280, 220)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.restore()
            self.body(ctx, t)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(11)
            ctx.stroke()
            on = int(t * 6) % 2
            for k, c in enumerate(((0.95, 0.15, 0.2), (0.2, 0.4, 1.0))):
                lit = (k == on)
                _rrect(ctx, -30 + k * 45, -345, 15 + k * 45, -315, 6)
                outline(ctx, c if lit else shade(c, 0.5), 5)
                if lit:
                    glow(ctx, -8 + k * 45, -330, 140, c, 0.55)
            ctx.select_font_face("DejaVu Sans", 0, 1)
            ctx.set_font_size(46)
            ctx.move_to(-95, -140)
            ctx.set_source_rgb(0.1, 0.15, 0.35)
            ctx.show_text("POLICE")
        if self.taxi:
            _rrect(ctx, -40, -350, 60, -315, 8)
            outline(ctx, (1, 1, 1), 5)
            ctx.save()
            self.body(ctx, t)
            ctx.clip()
            for k in range(12):
                ctx.rectangle(-330 + k * 55, -150, 27, 22)
            ctx.set_source_rgb(*INK)
            ctx.fill()
            ctx.restore()
        ctx.move_to(-80, -235)
        ctx.curve_to(-30, -305, 100, -305, 150, -235)
        ctx.close_path()
        outline(ctx, (0.55, 0.85, 1.0), 7)
        ctx.move_to(35, -300)
        ctx.line_to(35, -232)
        ctx.set_line_width(7)
        ctx.stroke()
        ellipse(ctx, -315, -165, 18, 12)
        outline(ctx, (1, 1, 0.7), 5)
        glow(ctx, -340, -165, 90, (1, 1, 0.7), 0.4)
        ctx.restore()
        _wheel(ctx, -200, -100, 62, t)
        _wheel(ctx, 210, -100, 62, t)

    def inside(self, ctx, t):
        for k in range(6):  # motor V6 con pistones
            y = -200 + 25 * math.sin(t * 16 + k * math.pi / 3)
            ctx.rectangle(150 + (k % 3) * 45, y - 25, 32, 50)
            ctx.set_source_rgb(0.8, 0.82, 0.88)
            ctx.fill()
        glow(ctx, 220, -190, 110, (1, 0.5, 0.15), 0.7)
        flow_line(ctx, [(140, -170), (-100, -150), (-320, -130)], t * 2, (1, 0.6, 0.2), 8)
        for x in (-60, 40):
            ctx.arc(x, -250, 30, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.7)
            ctx.fill()


class Helicopter(Creature):
    float_ = True
    color = (0.2, 0.25, 0.4)

    def body(self, ctx, t):
        ctx.new_path()
        ellipse(ctx, -60, -420, 190, 120)

    def draw(self, ctx, t):
        ctx.move_to(100, -430)
        ctx.line_to(380, -470)
        ctx.line_to(380, -430)
        ctx.line_to(100, -380)
        ctx.close_path()
        outline(ctx, self.color)
        ctx.save()
        ctx.translate(380, -470)
        ctx.rotate(t * 30)
        for k in range(2):
            ctx.rotate(math.pi / 2)
            ctx.rectangle(-60, -6, 120, 12)
        ctx.restore()
        ctx.set_source_rgb(0.3, 0.3, 0.35)
        ctx.fill()
        for dx in (-130, 30):
            ctx.move_to(dx, -300)
            ctx.line_to(dx - 20, -250)
            ctx.move_to(-200, -250)
            ctx.line_to(80, -250)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(12)
        ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        ellipse(ctx, -140, -440, 80, 65)
        outline(ctx, (0.6, 0.9, 1.0), 7)
        ctx.move_to(-60, -540)
        ctx.line_to(-60, -580)
        ctx.set_line_width(14)
        ctx.stroke()
        w = abs(math.cos(t * 25))
        ellipse(ctx, -60, -585, 330 * w + 40, 14)
        ctx.set_source_rgba(0.2, 0.2, 0.25, 0.75)
        ctx.fill()
        a = 0.25 + 0.1 * math.sin(t * 3)  # foco buscando
        ctx.move_to(-120, -330)
        ctx.line_to(-330, 0)
        ctx.line_to(30, 0)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 0.75, a)
        ctx.fill()

    def inside(self, ctx, t):
        ctx.arc(-150, -430, 30, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.85, 0.7)
        ctx.fill()
        gear(ctx, 0, -420, 45, t * 8)
        flow_line(ctx, [(0, -420), (-60, -540)], t * 3, (1, 0.8, 0.3), 8)


class Motorcycle(Creature):
    color = (0.95, 0.3, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-200, -200), (-60, -300), (140, -290), (220, -200), (40, -160)])

    def draw(self, ctx, t):
        _speed_lines(ctx, t, 260, -300)
        _wheel(ctx, -200, -100, 85, t, 12)
        _wheel(ctx, 220, -100, 85, t, 12)
        ctx.move_to(220, -100)
        ctx.line_to(160, -330)
        ctx.line_to(110, -360)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(16)
        ctx.stroke()
        self.body(ctx, t)
        outline(ctx, self.color)
        _rrect(ctx, -150, -320, 40, -280, 18)
        outline(ctx, (0.15, 0.15, 0.17), 6)
        ctx.rectangle(-140, -200, 140, 60)
        outline(ctx, (0.75, 0.77, 0.82), 7)
        for k in range(3):
            ph = (t * 2 + k / 3) % 1
            ctx.arc(-260 - ph * 100, -150 + ph * 20, 18 + 24 * ph, 0, 2 * math.pi)
            ctx.set_source_rgba(0.7, 0.7, 0.75, 1 - ph)
            ctx.fill()

    def inside(self, ctx, t):
        for k in range(2):
            y = -175 + 18 * math.sin(t * 20 + k * math.pi)
            ctx.rectangle(-110 + k * 50, y - 20, 34, 40)
            ctx.set_source_rgb(0.8, 0.82, 0.88)
            ctx.fill()
        flow_line(ctx, [(-70, -170), (-200, -100)], t * 2, (1, 0.6, 0.2), 6)


class Speedboat(Creature):
    color = (1, 1, 1)

    def body(self, ctx, t):
        ctx.new_path()
        poly(ctx, [(-330, -250), (300, -250), (240, -130), (-260, -130)])

    def draw(self, ctx, t):
        ctx.save()
        ctx.translate(0, 8 * math.sin(t * 3))
        ctx.rotate(-0.05 + 0.03 * math.sin(t * 3))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(-300, -230, 590, 30)
        ctx.set_source_rgb(*NEON_PINK)
        ctx.fill()
        poly(ctx, [(-120, -250), (-40, -340), (90, -340), (90, -250)])
        outline(ctx, (0.6, 0.9, 1.0), 7)
        ctx.restore()
        for k in range(8):
            ph = (t * 2 + k / 8) % 1
            ctx.arc(300 + ph * 220, -140 - 60 * math.sin(ph * math.pi), 14 * (1 - ph) + 4, 0, 2 * math.pi)
            ctx.set_source_rgba(0.85, 0.95, 1, 1 - ph)
            ctx.fill()
        ctx.move_to(-450, -120)
        for x in range(-450, 451, 25):
            ctx.line_to(x, -120 + 10 * math.sin(x / 40 + t * 4))
        ctx.line_to(450, 0)
        ctx.line_to(-450, 0)
        ctx.close_path()
        ctx.set_source_rgba(0.2, 0.6, 0.9, 0.9)
        ctx.fill()

    def inside(self, ctx, t):
        gear(ctx, 220, -190, 40, t * 10)
        glow(ctx, 220, -190, 80, (1, 0.6, 0.2), 0.6)


class CashStack(Creature):
    color = (0.55, 0.85, 0.5)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-260, -330, 520, 330)

    def draw(self, ctx, t):
        glow(ctx, 0, -250, 330, (0.6, 1, 0.5), 0.35)
        for row in range(6):
            for col in range(3):
                x = -240 + col * 165
                y = -55 - row * 50
                _rrect(ctx, x, y, x + 150, y + 45, 6)
                outline(ctx, self.color, 5)
                ctx.rectangle(x + 55, y + 2, 40, 41)
                ctx.set_source_rgb(0.95, 0.95, 0.85)
                ctx.fill()
        for k in range(6):  # billetes volando
            ph = (t * 0.7 + k / 6) % 1
            ctx.save()
            ctx.translate(-200 + k * 80 + 40 * math.sin(t * 2 + k), -340 - ph * 380)
            ctx.rotate(t * 3 + k)
            ctx.scale(1, abs(math.cos(t * 4 + k)) + 0.2)
            ctx.rectangle(-55, -25, 110, 50)
            ctx.restore()
            outline(ctx, self.color, 4)
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(110)
        ctx.move_to(-40, -360)
        ctx.text_path("$")
        outline(ctx, (0.35, 0.75, 0.35), 7)

    def inside(self, ctx, t):
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(60)
        for k in range(8):
            ctx.move_to(-230 + (k % 4) * 120, -230 + (k // 4) * 120)
            ctx.set_source_rgba(1, 1, 0.6, 0.5 + 0.5 * abs(math.sin(t * 3 + k)))
            ctx.show_text("$")


class WantedStars(Creature):
    """Nivel de búsqueda: 6 estrellas que se van encendiendo."""
    float_ = True
    color = GOLD

    def body(self, ctx, t):
        ctx.new_path()
        ctx.rectangle(-330, -520, 660, 160)

    def draw(self, ctx, t):
        lit = min(6, int(t * 2.2) + 1)
        _rrect(ctx, -340, -530, 340, -350, 30)
        ctx.set_source_rgba(0, 0, 0, 0.55)
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(8)
        ctx.stroke()
        for k in range(6):
            x = -275 + k * 110
            on = k < lit
            flick = on and k == lit - 1 and int(t * 8) % 2
            ctx.save()
            ctx.translate(x, -440)
            s = 1.15 if (on and k == lit - 1) else 1.0
            ctx.scale(s, s)
            for j in range(10):
                a = -math.pi / 2 + j * math.pi / 5
                r = 44 if j % 2 == 0 else 19
                (ctx.move_to if j == 0 else ctx.line_to)(math.cos(a) * r, math.sin(a) * r)
            ctx.close_path()
            ctx.restore()
            outline(ctx, (1, 1, 1) if flick else (GOLD if on else (0.35, 0.35, 0.4)), 6)

    def inside(self, ctx, t):
        flow_line(ctx, [(-330, -440), (330, -440)], t * 2, (1, 0.3, 0.3), 6)


class Controller(Creature):
    color = (0.2, 0.2, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.move_to(-300, -380)
        ctx.curve_to(-300, -470, 300, -470, 300, -380)
        ctx.curve_to(330, -200, 260, -120, 200, -150)
        ctx.curve_to(150, -175, 120, -240, 0, -240)
        ctx.curve_to(-120, -240, -150, -175, -200, -150)
        ctx.curve_to(-260, -120, -330, -200, -300, -380)
        ctx.close_path()

    def draw(self, ctx, t):
        ctx.save()
        ctx.translate(0, -300)
        ctx.rotate(0.06 * math.sin(t * 6))
        ctx.translate(0, 300)
        self.body(ctx, t)
        outline(ctx, self.color)
        press = int(t * 4) % 4
        for k, c in enumerate(((1, 0.3, 0.3), (0.3, 0.85, 0.4), (0.3, 0.5, 1), (1, 0.85, 0.2))):
            dx, dy = ((0, -35), (35, 0), (0, 35), (-35, 0))[k]
            ctx.arc(190 + dx, -360 + dy, 24 if k != press else 20, 0, 2 * math.pi)
            outline(ctx, c if k != press else shade(c, 0.7), 5)
        ctx.rectangle(-225, -375, 90, 30)
        ctx.rectangle(-195, -405, 30, 90)
        ctx.set_source_rgb(0.4, 0.4, 0.45)
        ctx.fill()
        for x in (-80, 60):
            ctx.arc(x, -290, 38, 0, 2 * math.pi)
            outline(ctx, (0.35, 0.35, 0.4), 6)
        ctx.restore()

    def inside(self, ctx, t):
        ctx.rectangle(-60, -380, 120, 80)
        ctx.set_source_rgb(0.15, 0.35, 0.2)
        ctx.fill()
        for k in range(4):
            flow_line(ctx, [(-60, -360 + k * 18), (-200, -380 + k * 10)], t, (0.4, 1, 0.6), 3)
            flow_line(ctx, [(60, -360 + k * 18), (190, -380 + k * 10)], t, (0.4, 1, 0.6), 3)


class Console(Creature):
    color = (0.95, 0.95, 0.97)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -110, -660, 110, -60, 40)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        rrect(ctx, -40, -640, 40, -80, 20)
        ctx.set_source_rgb(0.12, 0.12, 0.15)
        ctx.fill()
        on = 0.5 + 0.5 * math.sin(t * 2)
        ctx.move_to(-35, -640)
        ctx.line_to(-35, -80)
        ctx.set_source_rgba(0.3, 0.6, 1, on)
        ctx.set_line_width(6)
        ctx.stroke()
        ctx.arc(0, -120, 12, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        rrect(ctx, -160, -70, 160, -20, 14)
        outline(ctx, self.color, 6)

    def inside(self, ctx, t):
        ctx.rectangle(-60, -450, 120, 120)
        ctx.set_source_rgb(0.25, 0.25, 0.3)
        ctx.fill()
        gear(ctx, 0, -560, 45, t * 12, (0.75, 0.8, 0.9))
        glow(ctx, 0, -390, 120, (1, 0.5, 0.3), 0.6)


class Vault(Creature):
    color = (0.7, 0.72, 0.78)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -280, -620, 280, -40, 30)

    def draw(self, ctx, t):
        open_ = max(0, math.sin(t * 0.9))
        self.body(ctx, t)
        outline(ctx, self.color)
        ctx.rectangle(-240, -580, 480, 500)
        ctx.set_source_rgb(0.15, 0.15, 0.18)
        ctx.fill()
        for k in range(9):  # lingotes y dinero dentro
            ctx.save()
            ctx.translate(-160 + (k % 3) * 160, -170 - (k // 3) * 110)
            poly(ctx, [(-60, 0), (60, 0), (45, -45), (-45, -45)])
            ctx.restore()
            outline(ctx, GOLD, 5)
        ctx.save()
        ctx.translate(-240, -330)
        ctx.scale(1 - open_ * 0.8, 1)
        ctx.arc(240, 0, 240, 0, 2 * math.pi)
        ctx.restore()
        outline(ctx, (0.8, 0.82, 0.88))
        ctx.save()
        ctx.translate(-240 + 240 * (1 - open_ * 0.8), -330)
        ctx.rotate(t * 2)
        for k in range(6):
            ctx.rotate(math.pi / 3)
            ctx.rectangle(-8, 0, 16, 110)
        ctx.restore()
        ctx.set_source_rgb(0.45, 0.47, 0.52)
        ctx.fill()

    def inside(self, ctx, t):
        for k in range(4):
            ctx.save()
            ctx.translate(-120 + k * 80, -330)
            ctx.rotate(t * (1 + k % 2) * (1 if k % 2 else -1))
            ctx.rectangle(-30, -6, 60, 12)
            ctx.restore()
            ctx.set_source_rgb(0.85, 0.85, 0.9)
            ctx.fill()


class NeonSign(Creature):
    """Cartel de neón retro (estilo Miami años 80): palmera y sol al atardecer."""
    float_ = True
    color = (0.1, 0.05, 0.2)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -280, -700, 280, -220, 30)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color)
        flick = 0.75 + 0.25 * (1 if math.sin(t * 13) > -0.9 else 0)
        ctx.save()
        ctx.arc(0, -470, 150, math.pi, 2 * math.pi)
        ctx.clip()
        for k in range(6):
            ctx.rectangle(-160, -620 + k * 26, 320, 13)
            ctx.set_source_rgba(*NEON_PINK, flick * (1 - k * 0.1))
            ctx.fill()
        ctx.restore()
        for k in range(4):
            ctx.move_to(-220, -440 + k * 20)
            ctx.line_to(220, -440 + k * 20)
        ctx.set_source_rgba(*NEON_CYAN, flick)
        ctx.set_line_width(5)
        ctx.stroke()
        ctx.move_to(90, -260)
        ctx.curve_to(100, -380, 80, -480, 120, -560)
        ctx.set_source_rgb(*NEON_CYAN)
        ctx.set_line_width(10)
        ctx.stroke()
        for k in range(5):
            a = -math.pi / 2 + (k - 2) * 0.6 + 0.06 * math.sin(t * 2 + k)
            ctx.move_to(120, -560)
            ctx.line_to(120 + math.cos(a) * 110, -560 + math.sin(a) * 60 + 50)
        ctx.set_line_width(8)
        ctx.stroke()
        glow(ctx, 0, -460, 330, NEON_PINK, 0.25 * flick)

    def inside(self, ctx, t):
        flow_line(ctx, [(-250, -680), (250, -680), (250, -240), (-250, -240), (-250, -680)], t, NEON_CYAN, 5)


class TVTrailer(Creature):
    """Pantalla con un tráiler y el contador de visitas disparado."""
    color = (0.15, 0.15, 0.18)

    def body(self, ctx, t):
        ctx.new_path()
        rrect(ctx, -320, -640, 320, -240, 24)

    def draw(self, ctx, t):
        ctx.rectangle(-20, -240, 40, 120)
        outline(ctx, self.color, 6)
        rrect(ctx, -150, -130, 150, -100, 10)
        outline(ctx, self.color, 6)
        self.body(ctx, t)
        outline(ctx, self.color)
        g = cairo.LinearGradient(0, -610, 0, -270)
        g.add_color_stop_rgb(0, 1.0, 0.45, 0.6)
        g.add_color_stop_rgb(1, 1.0, 0.75, 0.35)
        ctx.rectangle(-290, -610, 580, 340)
        ctx.set_source(g)
        ctx.fill()
        for k in range(4):
            x = ((t * 80 + k * 160) % 640) - 320
            ctx.move_to(x, -300)
            ctx.curve_to(x + 10, -380, x - 10, -440, x + 20, -480)
            ctx.set_source_rgb(0.15, 0.1, 0.2)
            ctx.set_line_width(10)
            ctx.stroke()
        ctx.move_to(-35, -480)
        ctx.line_to(-35, -400)
        ctx.line_to(35, -440)
        ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.fill()
        views = int(min(1, t / 3.5) ** 2 * 90_000_000)
        txt = f"{views:,}".replace(",", ".") + " visitas"
        ctx.select_font_face("DejaVu Sans", 0, 1)
        ctx.set_font_size(40)
        e = ctx.text_extents(txt)
        _rrect(ctx, -e.width / 2 - 20, -705, e.width / 2 + 20, -655, 14)
        ctx.set_source_rgb(0.95, 0.2, 0.25)
        ctx.fill()
        ctx.move_to(-e.width / 2 - e.x_bearing, -668)
        ctx.set_source_rgb(1, 1, 1)
        ctx.show_text(txt)

    def inside(self, ctx, t):
        for k in range(12):
            ph = (t * 0.9 + k / 12) % 1
            ctx.arc(-280 + k * 50, -270 - ph * 330, 10, 0, 2 * math.pi)
            ctx.set_source_rgba(1, 0.3, 0.4, 1 - ph)
            ctx.fill()


class Radar(Creature):
    """Minimapa circular con el punto del jugador y la policía acercándose."""
    float_ = True
    color = (0.2, 0.3, 0.25)

    def body(self, ctx, t):
        ctx.new_path()
        ctx.arc(0, -420, 230, 0, 2 * math.pi)

    def draw(self, ctx, t):
        self.body(ctx, t)
        outline(ctx, self.color, 14)
        ctx.save()
        self.body(ctx, t)
        ctx.clip()
        for k in range(-3, 4):
            ctx.move_to(-240, -420 + k * 70)
            ctx.line_to(240, -420 + k * 70 + 30)
            ctx.move_to(k * 70, -660)
            ctx.line_to(k * 70 - 30, -180)
        ctx.set_source_rgba(0.6, 0.75, 0.65, 0.6)
        ctx.set_line_width(12)
        ctx.stroke()
        ctx.move_to(0, -420)
        ctx.arc(0, -420, 240, t * 3, t * 3 + 0.5)
        ctx.close_path()
        ctx.set_source_rgba(0.5, 1, 0.6, 0.3)
        ctx.fill()
        for k in range(3):
            a = k * 2.1 + t * 0.5
            r = 180 - (t * 30) % 120
            on = int(t * 6) % 2
            ctx.arc(math.cos(a) * r, -420 + math.sin(a) * r, 16, 0, 2 * math.pi)
            ctx.set_source_rgb(*((0.95, 0.2, 0.25) if (k + on) % 2 else (0.25, 0.45, 1)))
            ctx.fill()
        ctx.restore()
        poly(ctx, [(0, -450), (22, -395), (0, -408), (-22, -395)])
        outline(ctx, (1, 1, 1), 5)

    def inside(self, ctx, t):
        flow_line(ctx, [(-200, -420), (0, -420), (150, -300)], t * 2, (1, 0.9, 0.3), 8)


GTA_THINGS = {
    "sports_car": SportsCar(), "police_car": SportsCar(color=(0.12, 0.12, 0.15), police=True),
    "taxi": SportsCar(color=(1.0, 0.85, 0.15), taxi=True), "helicopter": Helicopter(), "motorcycle": Motorcycle(),
    "speedboat": Speedboat(), "cash_stack": CashStack(), "wanted_stars": WantedStars(), "controller": Controller(),
    "console": Console(), "vault": Vault(), "neon_sign": NeonSign(), "tv_trailer": TVTrailer(), "radar_minimap": Radar(),
}

GTA_PARTS = {k: {"body": (0, -350), "head": (0, -580), "heart": (18, -345), "brain": (0, -590)} for k in GTA_PEOPLE}
GTA_PARTS.update({k: {"body": (0, -300), "engine": (200, -190), "core": (0, -400)} for k in GTA_THINGS})


# ============================================================ PAISAJES
def _art_deco(ctx, x, base, w, h, color, t, neon):
    ctx.rectangle(x, base - h, w, h)
    ctx.set_source_rgb(*color)
    ctx.fill_preserve()
    ctx.set_source_rgba(*INK, 0.5)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.rectangle(x + w * 0.3, base - h - 50, w * 0.4, 50)
    ctx.set_source_rgb(*shade(color, 0.95))
    ctx.fill()
    for k in range(3):
        ctx.rectangle(x, base - h + 40 + k * 22, w, 8)
        ctx.set_source_rgba(*neon, 0.85)
        ctx.fill()
    for wy in range(int(base - h + 120), int(base - 50), 60):
        for wx in range(int(x + 18), int(x + w - 30), 42):
            ctx.rectangle(wx, wy, 22, 34)
            ctx.set_source_rgba(1, 0.9, 0.6, 0.85 if hash((wx, wy)) % 3 else 0.25)
            ctx.fill()


def _neon_palm(ctx, x, base, s, t, color):
    sway = 0.05 * math.sin(t * 1.3 + x)
    ctx.save()
    ctx.translate(x, base)
    ctx.rotate(sway)
    ctx.move_to(0, 0)
    ctx.curve_to(15 * s, -150 * s, 5 * s, -280 * s, 30 * s, -380 * s)
    ctx.set_source_rgb(*color)
    ctx.set_line_width(14 * s)
    ctx.stroke()
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.55
        ctx.move_to(30 * s, -380 * s)
        ctx.curve_to(30 * s + math.cos(a) * 100 * s, -380 * s + math.sin(a) * 90 * s,
                     30 * s + math.cos(a) * 170 * s, -380 * s + math.sin(a) * 100 * s,
                     30 * s + math.cos(a) * 190 * s, -380 * s + math.sin(a) * 140 * s + 70 * s)
        ctx.set_line_width(12 * s)
        ctx.stroke()
    ctx.restore()


def L_vicecity_noche(ctx, t, feet):
    """Ciudad de Florida de noche: atardecer neón, edificios art déco, palmeras de neón."""
    g = cairo.LinearGradient(0, 0, 0, feet)
    g.add_color_stop_rgb(0, 0.12, 0.05, 0.28)
    g.add_color_stop_rgb(0.6, 0.65, 0.15, 0.55)
    g.add_color_stop_rgb(1, 1.0, 0.5, 0.35)
    ctx.set_source(g)
    ctx.paint()
    scenery.stars(ctx, t, 40, 500, 12)
    ctx.save()
    ctx.arc(540, feet - 420, 230, math.pi, 2 * math.pi)
    ctx.clip()
    for k in range(9):
        ctx.rectangle(300, feet - 660 + k * 28, 480, 16)
        ctx.set_source_rgb(1.0, 0.75 - k * 0.05, 0.3)
        ctx.fill()
    ctx.restore()
    cols = [(0.98, 0.75, 0.85), (0.7, 0.95, 0.9), (1.0, 0.92, 0.7), (0.8, 0.8, 1.0)]
    neons = [NEON_PINK, NEON_CYAN, (1, 0.9, 0.3), NEON_PINK]
    for k, x in enumerate((-30, 230, 620, 870)):
        _art_deco(ctx, x, feet - 120, 220, 520 + (k % 2) * 160, cols[k], t, neons[k])
    ctx.rectangle(0, feet - 120, 1080, 120)
    ctx.set_source_rgb(0.15, 0.12, 0.25)
    ctx.fill()
    for k in range(2):  # coches con luces pasando
        x = (t * (300 + k * 120) + k * 500) % 1400 - 200
        ctx.rectangle(x, feet - 70, 110, 35)
        ctx.set_source_rgb(*((1, 0.3, 0.6), (0.3, 0.9, 1))[k])
        ctx.fill()
        scenery_glow(ctx, x + 110, feet - 55, 70, (1, 1, 0.8), 0.5)
    for x in (60, 1000):
        _neon_palm(ctx, x, feet, 1.1, t, NEON_CYAN if x < 500 else NEON_PINK)
    scenery.ground(ctx, feet, (0.3, 0.25, 0.4))


def L_vicecity_playa(ctx, t, feet):
    """Playa de Florida de día: arena, mar turquesa, hoteles art déco pastel y palmeras."""
    scenery.sky(ctx, (0.3, 0.7, 1.0), (0.85, 0.95, 1.0), feet)
    scenery.sun(ctx, 880, 300, 85, t)
    scenery.clouds(ctx, t, 3, 260, 500)
    cols = [(1.0, 0.8, 0.85), (0.75, 0.95, 0.9), (1.0, 0.95, 0.75), (0.85, 0.85, 1.0), (1.0, 0.85, 0.7)]
    for k, x in enumerate(range(-40, 1100, 230)):
        _art_deco(ctx, x, feet - 330, 210, 260 + (k % 3) * 70, cols[k % 5], t, (NEON_PINK, NEON_CYAN)[k % 2])
    ctx.rectangle(0, feet - 330, 1080, 210)
    ctx.set_source_rgb(0.2, 0.75, 0.85)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(6)
    for k in range(3):
        y = feet - 300 + k * 60
        ctx.move_to(0, y)
        for x in range(0, 1081, 20):
            ctx.line_to(x, y + 8 * math.sin(x / 50 + t * 2 + k))
        ctx.stroke()
    scenery.ground(ctx, feet - 120, (0.98, 0.88, 0.65))
    for x in (90, 990):
        scenery.palm(ctx, x, feet - 40, 0.95, t)
    for k, c in enumerate(((1, 0.4, 0.5), (0.3, 0.7, 1))):  # sombrillas
        x = 330 + k * 380
        ctx.move_to(x, feet - 20)
        ctx.line_to(x, feet - 200)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(8)
        ctx.stroke()
        ctx.arc(x, feet - 200, 100, math.pi, 2 * math.pi)
        ctx.close_path()
        ctx.set_source_rgb(*c)
        ctx.fill()


def L_autopista(ctx, t, feet):
    """Autopista con coches a toda velocidad."""
    scenery.sky(ctx, (1.0, 0.6, 0.45), (1.0, 0.85, 0.6), feet - 300)
    scenery.sun(ctx, 540, feet - 380, 130, t, (1.0, 0.7, 0.3))
    scenery.building_row(ctx, feet - 300, t, [(0.55, 0.45, 0.6), (0.6, 0.5, 0.65)], 9, False, 150, 380)
    ctx.rectangle(0, feet - 300, 1080, 1920)
    ctx.set_source_rgb(0.3, 0.3, 0.34)
    ctx.fill()
    for y in (feet - 200, feet - 60):
        off = (t * 900) % 160
        for x in range(-160, 1240, 160):
            ctx.rectangle(x - off, y, 90, 14)
            ctx.set_source_rgb(1, 0.9, 0.3)
            ctx.fill()
    for k in range(3):
        x = (t * (500 + k * 160) + k * 450) % 1500 - 250
        y = feet - 280 + k * 90
        ctx.rectangle(x, y, 140, 45)
        ctx.set_source_rgb(*((0.95, 0.3, 0.6), (0.3, 0.6, 1), (1, 0.85, 0.2))[k])
        ctx.fill()
        for wx in (25, 115):
            ctx.arc(x + wx, y + 45, 16, 0, 2 * math.pi)
            ctx.set_source_rgb(*INK)
            ctx.fill()
    scenery.ground(ctx, feet + 120, (0.25, 0.25, 0.28))


def L_pantano(ctx, t, feet):
    """Manglares y pantanos de Florida, con caimanes asomando."""
    scenery.sky(ctx, (0.65, 0.85, 0.7), (0.9, 0.95, 0.8), feet)
    scenery.hills(ctx, feet - 360, 50, 0.006, (0.35, 0.55, 0.35), 1)
    for k in range(7):  # árboles de manglar
        x = 40 + k * 170
        for r in range(4):
            ctx.move_to(x, feet - 260)
            ctx.curve_to(x - 40 + r * 25, feet - 180, x - 60 + r * 40, feet - 140, x - 70 + r * 45, feet - 110)
        ctx.set_source_rgb(0.4, 0.3, 0.2)
        ctx.set_line_width(10)
        ctx.stroke()
        for dx, dy, r in ((0, -330, 80), (-60, -290, 55), (60, -290, 55)):
            ctx.new_sub_path()
            ctx.arc(x + dx, feet + dy, r, 0, 2 * math.pi)
        ctx.set_source_rgb(0.25, 0.5, 0.28)
        ctx.fill()
    ctx.rectangle(0, feet - 120, 1080, 1920)
    ctx.set_source_rgb(0.35, 0.5, 0.35)
    ctx.fill()
    for k in range(2):  # ojos de caimán
        x = 250 + k * 520 + 40 * math.sin(t * 0.5 + k)
        y = feet - 60
        ellipse(ctx, x, y, 70, 18)
        ctx.set_source_rgb(0.3, 0.45, 0.3)
        ctx.fill()
        for dx in (-25, 25):
            ctx.arc(x + dx, y - 14, 12, 0, 2 * math.pi)
            ctx.set_source_rgb(1, 0.85, 0.2)
            ctx.fill()
            ctx.rectangle(x + dx - 2, y - 24, 4, 20)
            ctx.set_source_rgb(*INK)
            ctx.fill()
    scenery.ground(ctx, feet, (0.4, 0.55, 0.35))


def L_banco(ctx, t, feet):
    """Interior de banco con cámara acorazada y alarma girando."""
    scenery.sky(ctx, (0.9, 0.88, 0.82), (0.82, 0.8, 0.75), feet)
    for x in (60, 950):
        scenery.rect(ctx, x, 200, 70, feet - 200, (0.95, 0.93, 0.88))
    ctx.arc(540, 640, 270, 0, 2 * math.pi)
    outline(ctx, (0.65, 0.67, 0.72), 12)
    ctx.arc(540, 640, 200, 0, 2 * math.pi)
    outline(ctx, (0.75, 0.77, 0.82), 8)
    ctx.save()
    ctx.translate(540, 640)
    ctx.rotate(t * 0.8)
    for k in range(6):
        ctx.rotate(math.pi / 3)
        ctx.rectangle(-10, 0, 20, 150)
    ctx.restore()
    ctx.set_source_rgb(0.45, 0.47, 0.52)
    ctx.fill()
    on = int(t * 4) % 2  # alarma
    ctx.arc(900, 260, 40, 0, 2 * math.pi)
    ctx.set_source_rgb(*((1, 0.2, 0.2) if on else (0.5, 0.15, 0.15)))
    ctx.fill()
    if on:
        glow(ctx, 900, 260, 300, (1, 0.2, 0.2), 0.35)
    scenery.rect(ctx, 0, feet - 220, 1080, 30, (0.55, 0.4, 0.3))
    scenery.ground(ctx, feet, (0.75, 0.72, 0.68))
    for x in range(0, 1080, 120):
        ctx.move_to(x, feet)
        ctx.line_to(x - 200, 1920)
    ctx.set_source_rgba(*INK, 0.15)
    ctx.set_line_width(4)
    ctx.stroke()


def L_salon_gamer(ctx, t, feet):
    """Habitación gamer de noche con la tele encendida y luces LED."""
    scenery.sky(ctx, (0.12, 0.1, 0.22), (0.2, 0.15, 0.3), feet)
    hue = (t * 0.2) % 1
    led = tuple(0.5 + 0.5 * math.sin(2 * math.pi * (hue + k / 3)) for k in range(3))
    ctx.rectangle(0, 120, 1080, 14)
    ctx.set_source_rgb(*led)
    ctx.fill()
    glow(ctx, 540, 130, 600, led, 0.25)
    scenery.rect(ctx, 190, 340, 700, 420, (0.08, 0.08, 0.1), 12)
    g = cairo.LinearGradient(0, 360, 0, 740)
    g.add_color_stop_rgb(0, 1.0, 0.45, 0.65)
    g.add_color_stop_rgb(1, 1.0, 0.75, 0.35)
    ctx.rectangle(215, 365, 650, 370)
    ctx.set_source(g)
    ctx.fill()
    for k in range(3):
        x = 215 + ((t * 120 + k * 220) % 650)
        ctx.move_to(x, 735)
        ctx.curve_to(x + 10, 640, x - 10, 560, x + 20, 500)
        ctx.set_source_rgb(0.15, 0.1, 0.2)
        ctx.set_line_width(10)
        ctx.stroke()
    glow(ctx, 540, 550, 520, (1, 0.6, 0.6), 0.25)
    scenery.rect(ctx, 150, 800, 780, 60, (0.25, 0.22, 0.28), 6)
    scenery.ground(ctx, feet, (0.3, 0.26, 0.35))


def scenery_glow(ctx, x, y, r, c, a):
    glow(ctx, x, y, r, c, a)


GTA_LANDSCAPES = {"vicecity_noche": L_vicecity_noche, "vicecity_playa": L_vicecity_playa, "autopista": L_autopista,
                  "pantano": L_pantano, "banco": L_banco, "salon_gamer": L_salon_gamer}
scenery.LANDSCAPES.update(GTA_LANDSCAPES)
scenery.DARK.update({"vicecity_noche", "salon_gamer"})

# opciones nuevas para los personajes que diseña la IA ("custom" con plantilla "person")
NEW_HATS = ["police_cap", "swat", "headphones", "hood", "biker", "beanie", "bandana", "visor"]
NEW_HOLDS = ["money_bag", "cash", "phone", "controller", "laptop", "handcuffs", "megaphone", "keys"]
NEW_EXTRAS = ["sunglasses", "gold_chain", "badge", "vest", "jacket", "tattoos", "hawaiian", "tank_top", "scar"]
NEW_FACES = ["masked"]
