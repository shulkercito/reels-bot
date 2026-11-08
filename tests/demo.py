"""Datos falsos para probar el montaje sin ninguna API."""
import subprocess

from PIL import Image, ImageDraw, ImageFont

import config

DEMO_SCRIPT = {
    "category": "demo",
    "style": "animado",
    "topic": "el cerebro se limpia al dormir",
    "title": "Tu cerebro se lava mientras duermes",
    "caption": "Mientras duermes, tu cerebro activa un sistema de limpieza. ¿Lo sabías?",
    "hashtags": ["#curiosidades", "#cerebro", "#sabiasque"],
    "scenes": [
        {"text": "Tu cerebro se lava a sí mismo.", "action": "shocked", "keyword": "¡SE LAVA!", "bg": "azul"},
        {"text": "Pesa solo un kilo y medio,", "action": "point", "bg": "amarillo",
         "chart": {"type": "bars", "title": "Peso del cerebro", "unit": "kg",
                   "items": [{"label": "Humano", "value": 1.4}, {"label": "Elefante", "value": 4.8}, {"label": "Gato", "value": 0.03}]}},
        {"text": "pero tiene ochenta y seis mil millones de neuronas.", "action": "think", "bg": "verde",
         "chart": {"type": "counter", "to": 86000000000, "title": "neuronas"}},
        {"text": "Durante el día acumula residuos.", "action": "talk", "creature": "human", "xray": True, "bg": "rosa",
         "zoom": {"of": "brain", "items": [{"kind": "cells", "label": "NEURONAS", "do": "pulse"},
                                           {"kind": "particles", "label": "RESIDUOS", "do": "gather"}]}},
        {"text": "Pero al dormir, las neuronas se encogen,", "action": "point", "creature": "human", "xray": True, "bg": "morado",
         "keyword": "SE ENCOGEN", "zoom": {"of": "brain", "items": [{"kind": "cells", "label": "NEURONAS", "do": "shrink"},
                                                                   {"kind": "fluid", "label": "LÍQUIDO", "do": "flow"}]}},
        {"text": "y el líquido cefalorraquídeo se lleva la basura.", "action": "celebrate", "creature": "human", "xray": True,
         "bg": "azul", "zoom": {"of": "brain", "items": [{"kind": "cells", "label": "NEURONAS", "do": "shrink"},
                                                        {"kind": "fluid", "label": "LÍQUIDO", "do": "flow"},
                                                        {"kind": "particles", "label": "RESIDUOS", "do": "exit"}]}},
        {"text": "Por eso dormir poco te deja la cabeza espesa.", "action": "sad", "second": "laugh", "bg": "naranja"},
        {"text": "¿Lo sabías? Te leo en comentarios.", "action": "wave", "props": ["brain", "star"], "bg": "amarillo"},
    ],
}

COLORS = [(20, 40, 90), (90, 20, 60), (20, 80, 70), (100, 60, 10), (40, 20, 100), (70, 70, 70)]


def fake_images(n: int, work: str) -> list:
    paths = []
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 140)
    for i in range(n):
        img = Image.new("RGB", (config.WIDTH, config.HEIGHT), COLORS[i % len(COLORS)])
        d = ImageDraw.Draw(img)
        for k in range(0, config.HEIGHT, 120):  # rayas para que se note el zoom
            d.line([(0, k), (config.WIDTH, k + 300)], fill=(255, 255, 255), width=3)
        d.text((config.WIDTH // 2, config.HEIGHT // 3), f"ESCENA {i + 1}", fill="white", font=font, anchor="mm")
        p = f"{work}/scene_{i:02d}.jpg"
        img.save(p, quality=92)
        paths.append(p)
    return paths


def fake_tts(text: str, out_mp3: str) -> list:
    """Tiempos inventados (~2.6 palabras/s) y un tono como 'voz'."""
    words, t = [], 0.2
    for w in text.split():
        d = 0.18 + 0.045 * len(w)
        words.append({"word": w, "start": t, "end": t + d})
        t += d + 0.06
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono", "-t", f"{t + 0.3:.2f}",
                    "-c:a", "libmp3lame", out_mp3], capture_output=True, check=True)
    return words


def fake_stickers(scenes: list, work: str):
    """Dibuja un pulpo cartoon sobre fondo blanco y lo pasa por el recorte real de pegatinas."""
    from src import stickers
    img = Image.new("RGB", (1024, 1024), (255, 255, 255))
    d = ImageDraw.Draw(img)
    purple, ink = (170, 90, 220), (25, 25, 30)
    for k in range(8):  # tentáculos
        x = 230 + k * 80
        d.line([(x, 560), (x - 40 + (k % 2) * 80, 760), (x + (k % 3 - 1) * 50, 900)], fill=ink, width=70, joint="curve")
        d.line([(x, 560), (x - 40 + (k % 2) * 80, 760), (x + (k % 3 - 1) * 50, 900)], fill=purple, width=50, joint="curve")
    d.ellipse([250, 150, 780, 640], fill=purple, outline=ink, width=14)
    for ex in (420, 610):
        d.ellipse([ex - 55, 330, ex + 55, 450], fill="white", outline=ink, width=10)
        d.ellipse([ex - 22, 370, ex + 22, 420], fill=ink)
    d.arc([440, 430, 590, 540], 20, 160, fill=ink, width=12)
    raw, png = f"{work}/subject_raw.jpg", f"{work}/subject_00.png"
    img.save(raw, quality=92)
    ok = stickers.cut_out(raw, png)
    for sc in scenes:
        if sc.get("subject"):
            sc["_sticker"] = png if ok else None
