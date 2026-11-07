"""Pegatinas del tema (un pulpo, un volcán...) generadas con IA gratis y recortadas.

Se pide un dibujo cartoon sobre fondo blanco, se elimina el fondo con un relleno
desde los bordes y se añade un borde blanco tipo pegatina + sombra.
"""
import os
import random
import time
import urllib.parse

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageOps

import config

STYLE = ("cute flat cartoon illustration, thick black outlines, simple bold shapes, vibrant colors, "
         "single subject centered, full body, isolated on pure plain white background, no text, no shadow")


def _download(subject: str, path: str) -> bool:
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(f"{subject}, {STYLE}")
    params = {"width": 1024, "height": 1024, "model": config.IMAGE_MODEL, "nologo": "true",
              "seed": random.randint(1, 10**6)}
    headers = {"Authorization": f"Bearer {config.POLLINATIONS_TOKEN}"} if config.POLLINATIONS_TOKEN else {}
    r = requests.get(url, params=params, headers=headers, timeout=180)
    if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 10_000:
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    print(f"[pegatina] fallo {r.status_code}")
    return False


def cut_out(src: str, dst: str, tol: int = 38) -> bool:
    """Quita el fondo blanco conectado con los bordes y crea la pegatina."""
    img = Image.open(src).convert("RGB")
    w, h = img.size
    marker = (255, 0, 255)
    flood = img.copy()
    # puntos de arranque repartidos por todo el borde
    seeds = [(x, y) for x in range(0, w, 32) for y in (0, h - 1)] + \
            [(x, y) for y in range(0, h, 32) for x in (0, w - 1)]
    for sx, sy in seeds:
        r, g, b = flood.getpixel((sx, sy))
        if min(r, g, b) > 200 and (r, g, b) != marker:
            ImageDraw.floodfill(flood, (sx, sy), marker, thresh=tol)
    mask = Image.new("L", (w, h), 255)
    px_f, px_m = flood.load(), mask.load()
    for y in range(h):
        for x in range(w):
            if px_f[x, y] == marker:
                px_m[x, y] = 0
    mask = mask.filter(ImageFilter.MedianFilter(5))
    bbox = mask.getbbox()
    if not bbox:
        return False
    cover = sum(1 for v in mask.getdata() if v) / (w * h)
    if cover < 0.04 or cover > 0.92:  # no se ha podido separar del fondo
        return False
    pad = 40
    bbox = (max(bbox[0] - pad, 0), max(bbox[1] - pad, 0), min(bbox[2] + pad, w), min(bbox[3] + pad, h))
    img, mask = img.crop(bbox), mask.crop(bbox)

    border = mask.filter(ImageFilter.MaxFilter(25))
    shadow = border.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste((0, 0, 0, 70), (0, 0), ImageOps.expand(shadow, 0).point(lambda v: v * 0.55))
    out = Image.alpha_composite(out, Image.new("RGBA", img.size, (0, 0, 0, 0)))
    white = Image.new("RGBA", img.size, (255, 255, 255, 255))
    out.paste(white, (0, -6), border)
    out.paste(img.convert("RGBA"), (0, -6), mask)
    out.save(dst)
    return True


def make(subject: str, work: str, idx: int):
    """Devuelve la ruta a la pegatina PNG o None si no se pudo."""
    raw, png = f"{work}/subject_{idx:02d}_raw.jpg", f"{work}/subject_{idx:02d}.png"
    for attempt in range(3):
        try:
            if _download(subject, raw) and cut_out(raw, png):
                return png
        except Exception as e:  # nunca rompe el vídeo: la escena sale sin pegatina
            print(f"[pegatina] error: {e}")
        time.sleep(5 * (attempt + 1))
    return None


def attach(scenes: list, work: str):
    """Genera una pegatina por cada 'subject' distinto y la asigna a sus escenas."""
    cache = {}
    for sc in scenes:
        subj = (sc.get("subject") or "").strip()
        if not subj:
            continue
        key = subj.lower()
        if key not in cache:
            print(f"[pegatina] {subj}")
            cache[key] = make(subj, work, len(cache))
        sc["_sticker"] = cache[key]
    ok = sum(1 for v in cache.values() if v)
    print(f"[pegatina] {ok}/{len(cache)} listas")
    if os.getenv("STICKERS_REQUIRED") == "true" and cache and not ok:
        raise RuntimeError("No se pudo generar ninguna pegatina")
