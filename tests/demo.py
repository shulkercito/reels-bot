"""Datos falsos para probar el montaje sin ninguna API."""
import subprocess

from PIL import Image, ImageDraw, ImageFont

import config

DEMO_SCRIPT = {
    "category": "demo",
    "style": "animado",
    "topic": "el pulpo y sus tres corazones",
    "title": "El animal con tres corazones",
    "caption": "Este animal tiene tres corazones y sangre azul. ¿Lo sabías?",
    "hashtags": ["#curiosidades", "#animales", "#sabiasque"],
    "scenes": [
        {"text": "Existe un animal con tres corazones.", "action": "shocked", "keyword": "¡3 CORAZONES!", "bg": "azul"},
        {"text": "Y probablemente lo has comido alguna vez.", "action": "laugh", "second": "shocked", "bg": "amarillo"},
        {"text": "Es el pulpo.", "action": "point", "keyword": "EL PULPO", "bg": "verde", "creature": "octopus"},
        {"text": "Dos corazones bombean sangre a las branquias,", "action": "talk", "bg": "rosa", "creature": "octopus", "xray": True},
        {"text": "y el tercero al resto del cuerpo.", "action": "point", "keyword": "+1", "bg": "naranja", "creature": "octopus", "xray": True},
        {"text": "¿Y su sangre?", "action": "think", "props": ["question"], "second": "shrug", "bg": "morado"},
        {"text": "Es azul, por una proteína con cobre.", "action": "shocked", "props": ["drop"], "keyword": "SANGRE AZUL", "bg": "azul", "creature": "octopus", "xray": True},
        {"text": "¿Lo sabías? Te leo en comentarios.", "action": "celebrate", "props": ["star", "star"], "second": "wave", "bg": "amarillo"},
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
