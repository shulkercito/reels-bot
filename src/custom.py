"""Modelos a medida que diseña la IA en cada vídeo, a partir de las plantillas (cuadrúpedo, ave, pez,
insecto, persona). Así hay animales y personajes nuevos sin dibujarlos a mano.

Ej.: {"template": "quadruped", "color": "marron", "ears": "round", "snout": "bear", "tail": "short",
      "pattern": "none", "extras": [], "legs": "short"}   -> un wombat
     {"template": "person", "skin": "light", "shirt": "azul", "hat": "bicorne", "hold": "sword", ...} -> Napoleón
"""
import hashlib
import json
import re

from src import creatures, people, zoo

COLORS = {
    "rojo": (0.92, 0.28, 0.28), "red": (0.92, 0.28, 0.28), "naranja": (1.0, 0.6, 0.2), "orange": (1.0, 0.6, 0.2),
    "amarillo": (1.0, 0.85, 0.25), "yellow": (1.0, 0.85, 0.25), "verde": (0.35, 0.75, 0.4), "green": (0.35, 0.75, 0.4),
    "azul": (0.3, 0.55, 0.95), "blue": (0.3, 0.55, 0.95), "celeste": (0.6, 0.82, 1.0), "morado": (0.6, 0.4, 0.9),
    "purple": (0.6, 0.4, 0.9), "rosa": (1.0, 0.65, 0.75), "pink": (1.0, 0.65, 0.75), "marron": (0.55, 0.36, 0.22),
    "brown": (0.55, 0.36, 0.22), "beige": (0.92, 0.82, 0.62), "gris": (0.6, 0.62, 0.66), "grey": (0.6, 0.62, 0.66),
    "gray": (0.6, 0.62, 0.66), "negro": (0.18, 0.18, 0.2), "black": (0.18, 0.18, 0.2), "blanco": (0.97, 0.97, 0.97),
    "white": (0.97, 0.97, 0.97), "dorado": (1.0, 0.8, 0.2), "gold": (1.0, 0.8, 0.2), "plateado": (0.8, 0.82, 0.86),
    "silver": (0.8, 0.82, 0.86), "granate": (0.6, 0.15, 0.2), "turquesa": (0.25, 0.8, 0.75), "teal": (0.25, 0.7, 0.7),
    "crema": (1.0, 0.95, 0.82), "cream": (1.0, 0.95, 0.82),
}
SKINS = {"light": people.SKIN, "clara": people.SKIN, "tan": (0.85, 0.65, 0.48), "morena": (0.85, 0.65, 0.48),
         "dark": (0.55, 0.38, 0.25), "oscura": (0.55, 0.38, 0.25), "green": (0.55, 0.9, 0.45), "grey": (0.75, 0.75, 0.78),
         "pale": (0.95, 0.93, 0.95)}

QUAD = dict(ears=["round", "pointy", "floppy", "big", "long", "small", "none"],
            snout=["dog", "cat", "bear", "cow", "pig", "long", "trunk", "hippo", "mouse"],
            tail=["thin", "bushy", "curly", "tuft", "long", "short", "none"],
            pattern=["none", "stripes", "spots", "patches", "giraffe", "panda"],
            extras=["mane", "horns", "antlers", "horn", "unicorn_horn", "tusks", "hump", "hooves", "ossicones"],
            legs=["short", "normal", "long"], body=["thin", "normal", "fat"])
BIRD = dict(beak=["short", "long", "hook", "flat", "big", "bent"], legs=["short", "long", "none"],
            tail=["fan", "long", "none"], extras=["mask", "comb", "ears"])
FISH = dict(flags=["teeth", "puff", "lure", "sword", "long"])
BUG = dict(wings=["none", "clear", "butterfly"], flags=["stinger", "tail", "pincers", "fly", "proboscis", "antenna"])
PERSON = dict(hat=["none", "helmet_space", "nemes", "knight", "tricorn", "viking", "crown", "wizard", "cowboy", "safari",
                   "chef", "roman", "fire", "samurai", "headband", "bicorne", "top_hat", "cap", "turban", "laurel"],
              hold=["none", "sword", "club", "wand", "flask", "shield", "ball", "torch", "flag", "cane", "spoon",
                    "binoculars", "katana", "hose", "book", "telescope", "spear", "bow", "trident", "microphone"],
              face=["normal", "robot", "alien", "skull", "mummy", "ninja", "zombie", "vampire", "ghost"],
              hair=["none", "short", "long", "messy", "bun", "wild"],
              extras=["coat", "stethoscope", "stripes", "collar", "bandages", "armor", "number", "emblem", "fur",
                      "diaper", "torn", "suit_panel", "glasses", "patch", "mustache", "backpack", "sleeves",
                      "medals", "tie", "toga"])

_CACHE = {}


def color(v, default):
    if isinstance(v, (list, tuple)) and len(v) == 3:
        try:
            return tuple(min(max(float(x) / (255 if max(v) > 1 else 1), 0), 1) for x in v)
        except (TypeError, ValueError):
            return default
    s = str(v or "").lower().strip()
    if re.fullmatch(r"#?[0-9a-f]{6}", s):
        s = s.lstrip("#")
        return tuple(int(s[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return COLORS.get(s, default)


def _pick(v, options, default):
    v = str(v or "").lower().strip()
    return v if v in options else default


def _flags(v, options):
    if isinstance(v, str):
        v = [v]
    return tuple(x for x in (str(i).lower().strip() for i in (v or [])) if x in options)


def build(spec):
    """Devuelve el nombre registrado del modelo a medida, o None si la especificación no vale."""
    if not isinstance(spec, dict):
        return None
    tpl = str(spec.get("template", "")).lower()
    key = "custom_" + hashlib.md5(json.dumps(spec, sort_keys=True, default=str).encode()).hexdigest()[:10]
    if key in _CACHE:
        return key
    obj, parts = None, None
    if tpl == "quadruped":
        legs = {"short": 110, "normal": 170, "long": 240}[_pick(spec.get("legs"), QUAD["legs"], "normal")]
        body = _pick(spec.get("body"), QUAD["body"], "normal")
        bry = {"thin": 85, "normal": 110, "fat": 145}[body]
        brx = {"thin": 180, "normal": 190, "fat": 225}[body]
        extras = _flags(spec.get("extras"), QUAD["extras"])
        neck = None
        head = (-170, -290 - bry - legs * 0.3, 85)
        if spec.get("long_neck"):
            head, neck = (-180, -720, 65), (-170, -690)
        obj = zoo.Quadruped(color=color(spec.get("color"), (0.75, 0.6, 0.45)), belly=color(spec.get("belly"), None),
                            ears=_pick(spec.get("ears"), QUAD["ears"], "round"),
                            snout=_pick(spec.get("snout"), QUAD["snout"], "dog"),
                            tail=_pick(spec.get("tail"), QUAD["tail"], "thin"),
                            pattern=None if _pick(spec.get("pattern"), QUAD["pattern"], "none") == "none"
                            else spec.get("pattern"),
                            pcolor=color(spec.get("pattern_color"), creatures.INK), extras=extras,
                            leg=legs, by=-(legs + bry * 0.55 + 10), brx=brx, bry=bry, legw=34 if body != "fat" else 50,
                            head=(head[0], -(legs + bry * 0.55 + 10) - bry * 0.9, head[2]) if not neck else head,
                            neck=neck)
    elif tpl == "bird":
        obj = zoo.BirdT(color=color(spec.get("color"), (0.4, 0.7, 0.95)), belly=color(spec.get("belly"), (0.95, 0.95, 0.95)),
                        beak=_pick(spec.get("beak"), BIRD["beak"], "short"), beakc=color(spec.get("beak_color"), (1.0, 0.7, 0.15)),
                        legs=_pick(spec.get("legs"), BIRD["legs"], "short"), fly=bool(spec.get("fly", True)),
                        crest=bool(spec.get("crest")), bigeyes=bool(spec.get("big_eyes")),
                        tail=_pick(spec.get("tail"), BIRD["tail"], "fan"),
                        neck=min(max(int(spec.get("neck") or 0), 0), 350), extras=_flags(spec.get("extras"), BIRD["extras"]),
                        y=-420 if spec.get("fly", True) else -260)
    elif tpl == "fish":
        f = _flags(spec.get("features"), FISH["flags"])
        obj = zoo.FishT(color=color(spec.get("color"), (1.0, 0.6, 0.2)), fins=color(spec.get("fin_color"), (0.9, 0.5, 0.2)),
                        stripes=color(spec.get("stripes"), None) if spec.get("stripes") else None,
                        teeth="teeth" in f, puff="puff" in f, lure="lure" in f, sword="sword" in f, long="long" in f)
    elif tpl == "bug":
        f = _flags(spec.get("features"), BUG["flags"])
        wings = _pick(spec.get("wings"), BUG["wings"], "none")
        fly = "fly" in f or wings != "none"
        obj = zoo.BugT(color=color(spec.get("color"), (0.3, 0.25, 0.22)), legs=8 if spec.get("legs") == 8 else 6,
                       wings=None if wings == "none" else wings, wingc=color(spec.get("wing_color"), (0.85, 0.95, 1.0)),
                       stripes=color(spec.get("stripes"), None) if spec.get("stripes") else None,
                       spots=color(spec.get("spots"), None) if spec.get("spots") else None,
                       stinger="stinger" in f, tail="tail" in f, pincers="pincers" in f, fly=fly,
                       proboscis="proboscis" in f, antenna="antenna" in f or (not f and spec.get("legs") != 8), y=-400 if fly else -160)
    elif tpl == "person":
        hair = spec.get("hair")
        hair_kind = _pick(hair[0] if isinstance(hair, list) and hair else hair, PERSON["hair"], "none")
        hair_col = color(hair[1] if isinstance(hair, list) and len(hair) > 1 else spec.get("hair_color"), (0.3, 0.2, 0.12))
        face = _pick(spec.get("face"), PERSON["face"], "normal")
        obj = people.Person(skin=SKINS.get(str(spec.get("skin", "")).lower(), color(spec.get("skin"), people.SKIN)),
                            shirt=color(spec.get("shirt"), (0.3, 0.5, 0.9)), pants=color(spec.get("pants"), (0.3, 0.35, 0.55)),
                            hat=None if _pick(spec.get("hat"), PERSON["hat"], "none") == "none" else spec.get("hat"),
                            hold=None if _pick(spec.get("hold"), PERSON["hold"], "none") == "none" else spec.get("hold"),
                            face=face, beard=color(spec.get("beard"), None) if spec.get("beard") else None,
                            hair=None if hair_kind == "none" else (hair_kind, hair_col),
                            cape=color(spec.get("cape"), None) if spec.get("cape") else None,
                            extras=_flags(spec.get("extras"), PERSON["extras"]), wave=bool(spec.get("wave")),
                            float_=face == "ghost",
                            inside={"robot": "robot", "ghost": "ghost", "skull": "skeleton"}.get(face, "human"))
        parts = people.PEOPLE_PARTS["astronaut"]
    if obj is None:
        return None
    creatures.CREATURES[key] = obj
    creatures.PARTS[key] = parts or zoo._parts(key, obj)
    _CACHE[key] = spec
    return key


def prompt_help():
    return (
        '    {"template": "quadruped", "color": C, "belly": C, "ears": ' + "/".join(QUAD["ears"]) +
        ', "snout": ' + "/".join(QUAD["snout"]) + ', "tail": ' + "/".join(QUAD["tail"]) +
        ', "pattern": ' + "/".join(QUAD["pattern"]) + ', "pattern_color": C, "extras": [' + ", ".join(QUAD["extras"]) +
        '], "legs": short/normal/long, "body": thin/normal/fat, "long_neck": bool}\n'
        '    {"template": "bird", "color": C, "belly": C, "beak": ' + "/".join(BIRD["beak"]) +
        ', "beak_color": C, "legs": short/long/none, "fly": bool, "crest": bool, "big_eyes": bool, "tail": fan/long/none,'
        ' "neck": 0-350, "extras": [mask, comb, ears]}\n'
        '    {"template": "fish", "color": C, "fin_color": C, "stripes": C o null, "features": [teeth, puff, lure, sword, long]}\n'
        '    {"template": "bug", "color": C, "legs": 6/8, "wings": none/clear/butterfly, "wing_color": C, "stripes": C,'
        ' "spots": C, "features": [stinger, tail, pincers, fly, proboscis, antenna]}\n'
        '    {"template": "person", "skin": light/tan/dark/pale/green, "shirt": C, "pants": C, "hat": ' + "/".join(PERSON["hat"]) +
        ', "hold": ' + "/".join(PERSON["hold"]) + ', "face": ' + "/".join(PERSON["face"]) +
        ', "hair": [short/long/messy/bun/wild, C], "beard": C o null, "cape": C o null, "extras": [' +
        ", ".join(PERSON["extras"]) + '], "wave": bool}\n'
        '    C = color: ' + ", ".join(k for k in COLORS if not re.match(r"^[a-z]+$", k) or k in
                                         ("rojo", "naranja", "amarillo", "verde", "azul", "celeste", "morado", "rosa",
                                          "marron", "beige", "gris", "negro", "blanco", "dorado", "plateado", "granate",
                                          "turquesa", "crema")) + ' o "#rrggbb"'
    )
