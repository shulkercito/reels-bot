"""Datos falsos para probar el montaje sin ninguna API."""
import subprocess

from PIL import Image, ImageDraw, ImageFont

import config

DEMO_SCRIPT = {
    "category": "demo",
    "topic": "el pulpo y sus tres corazones",
    "title": "El animal con tres corazones",
    "caption": "Este animal tiene tres corazones y sangre azul. ¿Lo sabías?",
    "hashtags": ["#curiosidades", "#animales", "#sabiasque"],
    "scenes": [
        {"text": "Existe un animal con tres corazones y sangre azul.", "image_prompt": "octopus"},
        {"text": "Y probablemente lo has comido alguna vez.", "image_prompt": "plate"},
        {"text": "Es el pulpo. Dos corazones bombean sangre a las branquias,", "image_prompt": "gills"},
        {"text": "y el tercero al resto del cuerpo.", "image_prompt": "heart"},
        {"text": "Su sangre es azul por la hemocianina, una proteína con cobre.", "image_prompt": "blue"},
        {"text": "¿Sabías esto? Te leo en comentarios.", "image_prompt": "end"},
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
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={t + 0.3:.2f}",
                    "-c:a", "libmp3lame", out_mp3], capture_output=True, check=True)
    return words
