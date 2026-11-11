"""Prueba de robustez del guion: le pasa datos basura (como si la IA se equivocara) al limpiador
y comprueba que la escena resultante siempre se puede dibujar.  Uso: python -m tests.fuzz_guion"""
import random
import sys
import traceback

import cairo

from src import anim, script_gen

JUNK = [None, "", 0, -3, 1e9, "abc", "#zzzzzz", "#12", [], {}, ["a", None, 3], {"x": 1}, True, "custom", [1, 2, 3],
        [300, 0, 0], "long", "none", float("nan")]
KEYS = {"quadruped": ["color", "belly", "ears", "snout", "tail", "pattern", "pattern_color", "extras", "legs", "body", "long_neck"],
        "bird": ["color", "belly", "beak", "beak_color", "legs", "fly", "crest", "big_eyes", "tail", "neck", "extras"],
        "fish": ["color", "fin_color", "stripes", "features"],
        "bug": ["color", "legs", "wings", "wing_color", "stripes", "spots", "features"],
        "person": ["skin", "shirt", "pants", "hat", "hold", "face", "hair", "hair_color", "beard", "cape", "extras", "wave"]}


def main(n=500, seed=3):
    rnd = random.Random(seed)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, anim.W, anim.H)
    ctx = cairo.Context(surf)
    bad = 0
    for k in range(n):
        tpl = rnd.choice(list(KEYS) + ["nope", None, 7])
        spec = {"template": tpl}
        for key in KEYS.get(tpl if isinstance(tpl, str) else "", []):
            if rnd.random() < 0.7:
                spec[key] = rnd.choice(JUNK)
        sc = {"text": "hola mundo", "action": rnd.choice(JUNK), "props": rnd.choice(JUNK + [["heart", "zzz", 5, None]]),
              "second": rnd.choice(JUNK), "keyword": rnd.choice(JUNK),
              "creature": rnd.choice(JUNK + ["octopus", "Black Hole", "qwerty"]),
              "custom": rnd.choice([spec, spec, None, "x", [spec]]), "icon": rnd.choice(JUNK + ["violin"]),
              "xray": rnd.choice(JUNK),
              "zoom": rnd.choice(JUNK + [{"items": JUNK}, {"of": 3, "items": [{"kind": "cells", "do": 7, "label": None, "color": []}]}]),
              "chart": rnd.choice(JUNK + [{"type": "bars", "items": JUNK}, {"type": "counter", "to": "mil"},
                                          {"type": "bars", "items": [{"label": None, "value": "1,5"}, {"value": None}, {"label": 3, "value": "2"}]}]),
              "scene": rnd.choice(JUNK + ["Playa"]), "bg": rnd.choice(JUNK)}
        try:
            script_gen._clean_anim([{"text": "a", "bg": "azul"}, sc])
            for t in (0.0, 1.2):
                ctx.save()
                anim.draw_scene(ctx, sc, t, 3.0, k)
                ctx.restore()
        except Exception:
            bad += 1
            if bad <= 8:
                print("FALLO", traceback.format_exc().splitlines()[-2:], sc)
            ctx = cairo.Context(surf)
    print(f"{n} escenas basura probadas, {bad} con fallo")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
