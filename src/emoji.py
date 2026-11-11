"""Biblioteca de ~1.600 iconos (Fluent Emoji de Microsoft, licencia MIT) para "casi todo".

- find("violin") -> nombre del icono que mejor encaja (o None)
- surface(nombre, tamaño) -> superficie cairo con contorno oscuro al estilo de los monigotes
"""
import difflib
import io
import json
import math
import os
import re
import tarfile

import cairo

BUNDLE = os.path.join(os.path.dirname(__file__), "..", "assets", "emoji", "emoji.tar.xz")
INK = (0.11, 0.11, 0.13)
_INDEX = None
_SVG = {}
_SURF = {}
_WORDS = None
_FULL = None

# alias en español/inglés que la IA podría usar y no están literalmente en el índice
ALIASES = {
    "dinero": "money_bag", "money": "money_bag", "gold": "coin", "virus": "microbe", "bacteria": "microbe",
    "vaccine": "syringe", "vacuna": "syringe", "medicine": "pill", "pills": "pill", "brain": "brain",
    "skull": "skull", "bone": "bone", "blood": "drop_of_blood", "dna": "dna", "planet": "ringed_planet",
    "earth": "globe_showing_europe_africa", "world": "globe_showing_europe_africa", "fire": "fire",
    "music": "musical_note", "phone": "mobile_phone", "computer": "laptop", "car": "automobile",
    "police": "police_car", "ambulance": "ambulance", "rocket": "rocket", "ship": "ship", "boat": "sailboat",
    "plane": "airplane", "train": "locomotive", "bike": "bicycle", "castle": "castle", "church": "church",
    "pyramid": "desert", "mummy": "mage", "king": "crown", "queen": "crown", "trophy": "trophy",
    "medal": "1st_place_medal", "gun": "water_pistol", "sword": "crossed_swords", "war": "crossed_swords",
    "bomb": "bomb", "nuclear": "radioactive", "radiation": "radioactive", "poison": "skull_and_crossbones",
    "clock": "alarm_clock", "time": "hourglass_done", "calendar": "calendar", "law": "balance_scale",
    "justice": "balance_scale", "book": "open_book", "school": "school", "university": "graduation_cap",
    "science": "test_tube", "lab": "test_tube", "chemistry": "test_tube", "math": "abacus", "idea": "light_bulb",
    "love": "red_heart", "heart": "anatomical_heart", "sleep": "zzz", "dream": "thought_balloon", "eye": "eye",
    "ear": "ear", "nose": "nose", "tooth": "tooth", "lungs": "lungs", "muscle": "flexed_biceps", "gym": "flexed_biceps",
    "running": "person_running", "football": "soccer_ball", "soccer": "soccer_ball", "basketball": "basketball",
    "tennis": "tennis", "olympics": "sports_medal", "mountain": "mountain", "volcano": "volcano", "island": "desert_island",
    "beach": "beach_with_umbrella", "rain": "cloud_with_rain", "storm": "cloud_with_lightning_and_rain",
    "snow": "snowflake", "ice": "ice", "sun": "sun", "moon": "crescent_moon", "star": "star", "galaxy": "milky_way",
    "comet": "comet", "alien": "alien", "robot": "robot", "ghost": "ghost", "monster": "ogre", "dragon": "dragon",
    "unicorn": "unicorn", "dinosaur": "t_rex", "trex": "t_rex", "mammoth": "mammoth", "chocolate": "chocolate_bar",
    "coffee": "hot_beverage", "beer": "beer_mug", "wine": "wine_glass", "bread": "bread", "cheese": "cheese_wedge",
    "egg": "egg", "milk": "glass_of_milk", "salt": "salt", "sugar": "candy", "oil": "oil_drum", "gas": "fuel_pump",
    "electricity": "high_voltage", "lightning": "high_voltage", "battery": "battery", "magnet": "magnet",
    "microscope": "microscope", "telescope": "telescope", "map": "world_map", "treasure": "gem_stone",
    "diamond": "gem_stone", "prison": "locked", "lock": "locked", "key": "key", "money_bag": "money_bag",
    "meteor": "comet", "meteorite": "comet", "asteroid": "rock", "tsunami": "water_wave", "wave": "water_wave",
    "ocean": "water_wave", "sea": "water_wave", "fossil": "bone", "titanic": "ship", "honey": "honey_pot",
    "pharaoh": "crown", "emperor": "crown", "soldier": "military_helmet", "army": "military_helmet",
    "president": "classical_building", "government": "classical_building", "museum": "classical_building",
    "hospital": "hospital", "doctor": "stethoscope", "surgery": "syringe", "cancer": "microbe", "covid": "microbe",
    "insect": "beetle", "bug": "lady_beetle", "worm": "worm", "fungus": "mushroom", "plant": "seedling",
    "forest": "evergreen_tree", "desert": "desert", "city": "cityscape", "factory": "factory", "pollution": "factory",
    "climate": "thermometer", "temperature": "thermometer", "heat": "thermometer", "cold": "cold_face",
    "internet": "globe_with_meridians", "wifi": "antenna_bars", "ai": "robot", "video game": "video_game",
    "game": "video_game", "camera": "camera", "photo": "camera", "movie": "clapper_board", "cinema": "clapper_board",
    "tv": "television", "radio": "radio", "news": "newspaper", "letter": "envelope", "mail": "envelope",
    "gold bars": "coin", "gold bar": "coin", "red blood cells": "drop_of_blood", "protein shake": "cup_with_straw",
    "dumbbell": "flexed_biceps", "barbell": "flexed_biceps", "weights": "flexed_biceps", "vulture": "eagle",
}


def _load():
    global _INDEX, _WORDS, _FULL
    if _INDEX is not None:
        return
    _INDEX = {}
    if not os.path.exists(BUNDLE):
        print("[emoji] no se encuentra la biblioteca de iconos; se usarán solo los dibujos propios")
        return
    with tarfile.open(BUNDLE, "r:xz") as tar:
        for m in tar.getmembers():
            if m.name == "index.json":
                _INDEX = json.load(tar.extractfile(m))
            elif m.name.startswith("svg/"):
                _SVG[m.name[4:-4]] = tar.extractfile(m).read()
    _WORDS = {}
    _FULL = {}
    parts = {}
    for k, v in _INDEX.items():
        for w in [v["name"]] + v["keywords"]:
            _WORDS.setdefault(w, k)
            _FULL.setdefault(w, k)
        for part in re.split(r"[^a-z0-9]+", v["name"]):
            if len(part) > 2:
                parts.setdefault(part, []).append(k)
    for part, cands in parts.items():
        if part in _WORDS:
            continue
        # prefiere el icono cuyo nombre EMPIEZA por esa palabra y, si no, el de nombre más corto
        cands.sort(key=lambda c: (not c.startswith(part), len(c)))
        _WORDS[part] = cands[0]


USEFUL_SYMBOLS = {"warning", "radioactive", "biohazard", "recycling_symbol", "prohibited", "no_entry", "high_voltage",
                  "check_mark_button", "cross_mark", "question_mark", "exclamation_mark", "red_question_mark",
                  "red_exclamation_mark", "infinity", "trident_emblem", "atom_symbol", "peace_symbol", "yin_yang",
                  "medical_symbol", "hundred_points", "dollar_banknote", "euro_banknote", "heavy_dollar_sign"}


def catalog_names():
    """Nombres útiles para darle a la IA (sin caras repetidas, relojes, letras ni variantes de género)."""
    _load()
    out = []
    names = set(_INDEX)
    for k, v in _INDEX.items():
        g = v["group"]
        if g == "Symbols" and k not in USEFUL_SYMBOLS:
            continue
        if g == "Smileys & Emotion" and ("face" in k or k.endswith("heart") or "cat_" in k):
            continue
        if re.search(r"(oclock|thirty)$", k):
            continue
        if g == "People & Body" and re.match(r"(man|woman)_", k):
            if "person_" + k.split("_", 1)[1] in names or k.split("_", 1)[1] in names:
                continue
        out.append(k)
    return sorted(out)


def available():
    _load()
    return bool(_INDEX)


def group(name):
    _load()
    return (_INDEX.get(name) or {}).get("group", "")


def find(term):
    """Busca el icono que mejor representa un término (en inglés preferentemente)."""
    _load()
    if not _INDEX or not isinstance(term, str):
        return None
    t = term.lower().strip()
    if len(t) < 3 or not re.search(r"[a-z]{3}", t):
        return None
    r = _find(t)
    return r if r in _useful() else None


_USEFUL = None


def _useful():
    global _USEFUL
    if _USEFUL is None:
        _USEFUL = set(catalog_names())
    return _USEFUL


def _find(t):
    s = re.sub(r"[^a-z0-9]+", "_", t).strip("_")
    if s in _INDEX:
        return s
    if s in ALIASES and ALIASES[s] in _INDEX:
        return ALIASES[s]
    if t in _WORDS:
        return _WORDS[t]
    # varias palabras: "ancient egyptian pharaoh" -> prueba cada palabra empezando por la última
    words = [w for w in re.split(r"[^a-z0-9]+", t) if len(w) > 2]
    if t in ALIASES and ALIASES[t] in _INDEX:
        return ALIASES[t]
    # frase de varias palabras: solo coincidencias exactas por palabra (evita "gold bars" -> antenna_bars)
    multi = len(words) > 1
    for w in reversed(words):
        sing = w[:-1] if w.endswith("s") and len(w) > 3 else w
        for cand in (w, sing):
            if cand in ALIASES and ALIASES[cand] in _INDEX:
                return ALIASES[cand]
            if cand in _INDEX:
                return cand
            if cand in (_FULL if multi else _WORDS):
                return (_FULL if multi else _WORDS)[cand]
    close = difflib.get_close_matches(s, list(_INDEX), n=1, cutoff=0.82)
    return close[0] if close else None


def surface(name, size=420, outline=True):
    """Icono como superficie cairo, con contorno oscuro grueso (estilo de los monigotes)."""
    key = (name, size, outline)
    if key in _SURF:
        return _SURF[key]
    _load()
    svg = _SVG.get(name)
    if svg is None:
        return None
    import cairosvg
    png = cairosvg.svg2png(bytestring=svg, output_width=size, output_height=size)
    img = cairo.ImageSurface.create_from_png(io.BytesIO(png))
    if not outline:
        _SURF[key] = img
        return img
    pad = max(10, size // 28)
    out = cairo.ImageSurface(cairo.FORMAT_ARGB32, size + pad * 2, size + pad * 2)
    c = cairo.Context(out)
    pat = cairo.SurfacePattern(img)
    for k in range(16):  # contorno: la silueta repetida en círculo, en tinta oscura
        a = k * math.pi / 8
        c.save()
        c.translate(pad + math.cos(a) * pad * 0.8, pad + math.sin(a) * pad * 0.8)
        c.set_source_rgb(*INK)
        c.mask(pat)
        c.restore()
    c.set_source_surface(img, pad, pad)
    c.paint()
    out.flush()
    _SURF[key] = out
    return out


def draw(ctx, name, cx, cy, size, t, k=1.0, lively=False, shake=0.0, rot=0.0):
    """Dibuja el icono centrado en (cx, cy) con su animación base."""
    surf = surface(name, 420)
    if surf is None:
        return False
    w = surf.get_width()
    s = size / w * k
    squash = 1 + (0.06 if lively else 0.03) * math.sin(t * (5 if lively else 2.5))
    hop = -abs(math.sin(t * 3.2)) * size * 0.12 if lively else 6 * math.sin(t * 2)
    ctx.save()
    ctx.translate(cx + shake * 10 * math.sin(t * 70), cy + hop)
    ctx.rotate(rot + (0.06 if lively else 0.04) * math.sin(t * 1.9))
    ctx.scale(s / squash, s * squash)
    ctx.set_source_surface(surf, -w / 2, -w / 2)
    ctx.paint()
    ctx.restore()
    return True
