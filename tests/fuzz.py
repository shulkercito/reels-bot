"""Prueba de robustez: dibuja todas las combinaciones (modelos, paisajes, acciones, lupas, iconos)
en varios instantes y avisa de cualquier fallo.  Uso: python -m tests.fuzz"""
import random
import sys
import traceback

import cairo

from src import anim, catalog, creatures, emoji, explain, scenery  # noqa: F401


def main(n_random=300, seed=1):
    rnd = random.Random(seed)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, anim.W, anim.H)
    ctx = cairo.Context(surf)
    lands = list(scenery.LANDSCAPES) + [""]
    icons = emoji.catalog_names()
    cases = []
    for i, cr in enumerate(creatures.CREATURES):  # todos los modelos, normal y rayos X
        for xr in (False, True):
            cases.append({"action": anim.ACTIONS[i % len(anim.ACTIONS)], "creature": cr, "xray": xr,
                          "scene": lands[i % len(lands)], "bg": "azul", "keyword": "PRUEBA"})
    for _ in range(n_random):
        kinds = rnd.sample(explain.KINDS, rnd.randint(1, 4))
        sc = {"action": rnd.choice(anim.ACTIONS), "scene": rnd.choice(lands), "bg": rnd.choice(list(anim.BACKGROUNDS)),
              "keyword": rnd.choice(["", "DATO", "¡UNA PALABRA MUY LARGA AQUÍ!"]),
              "second": rnd.choice(["", ""] + anim.ACTIONS),
              "props": rnd.sample(anim.PROPS, rnd.randint(0, 3)) + (["emoji:" + rnd.choice(icons)] if icons and rnd.random() < .3 else [])}
        r = rnd.random()
        if r < 0.35:
            sc["creature"] = rnd.choice(list(creatures.CREATURES))
            sc["xray"] = rnd.random() < 0.5
        elif r < 0.6 and icons:
            sc["icon"] = rnd.choice(icons)
        r = rnd.random()
        if r < 0.3:
            sc["zoom"] = {"of": rnd.choice(["brain", "heart", "", "body", "nope"]),
                          "items": [{"kind": k, "label": k.upper(), "do": rnd.choice(explain.DOS[k])} for k in kinds]}
        elif r < 0.45:
            sc["chart"] = rnd.choice([
                {"type": "bars", "title": "T", "unit": "kg", "items": [{"label": "a", "value": 0}, {"label": "b", "value": 0}]},
                {"type": "bars", "title": "Un título bastante largo para probar", "items": [{"label": "x" * 16, "value": -5}, {"label": "y", "value": 1e12}, {"label": "z", "value": 0.001}, {"label": "w", "value": 3}]},
                {"type": "counter", "to": 0}, {"type": "counter", "to": 1e15, "prefix": "$", "suffix": " km/h", "title": "x"}])
        cases.append(sc)
    bad = 0
    for i, sc in enumerate(cases):
        for t in (0.0, 0.05, 0.4, 1.3, 4.0):
            try:
                ctx.save()
                anim.draw_scene(ctx, sc, t, 4.0, i)
                ctx.restore()
            except Exception:
                bad += 1
                print("FALLO", {k: v for k, v in sc.items() if k != "props"}, "t=", t)
                print(traceback.format_exc().splitlines()[-1])
                ctx = cairo.Context(surf)
                break
    print(f"{len(cases)} escenas probadas, {bad} con fallo")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
