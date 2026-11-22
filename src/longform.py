"""Vídeo LARGO horizontal (1920x1080, ~8-10 min): varias historias del mismo tema seguidas, con capítulos.

Reutiliza todo el bot (guion verificado, voz, animación, música) y cambia el formato:
- cada historia se escribe y verifica por separado y es un capítulo,
- la escena vertical se encaja en el centro y los lados se rellenan con el mismo paisaje en espejo,
- arriba sale el capítulo y el contador "3/10" (ayuda a que la gente se quede hasta el final),
- se generan título, descripción con capítulos y miniatura.
"""
import datetime as dt
import json
import math
import os
import random
import subprocess

import cairo

import config
from src import anim, render, script_gen, subtitles

WW, HH = 1920, 1080
TOP = 250                       # parte de arriba de la escena vertical que se recorta
S = HH / (anim.FEET + 100 - TOP)  # escala para que quepan del cielo al suelo
CW = anim.W * S                 # ancho de la escena central
CX = (WW - CW) / 2

THEMES = [
    "estafas y golpes maestros increíbles (cómo lo hicieron y cómo los pillaron)",
    "historias reales tan locas que parecen inventadas",
    "oficios antiguos rarísimos que ya no existen",
    "¿por qué...? explicaciones sorprendentes de cosas de todos los días",
    "personas con una suerte (buena o mala) increíble",
    "inventos que nacieron por accidente",
    "millonarios y fortunas absurdas",
    "leyendas del fútbol: anécdotas que parecen mentira",
]

LONG_NOTES = (
    "Esta historia es el capítulo {n} de {total} de un vídeo LARGO de YouTube sobre: {theme}. "
    "Tiene que ser una historia DISTINTA a estas, que ya salen en el vídeo: {done}. "
    "Elige historias MUY conocidas y bien documentadas (con persona, año y lugar reales que salgan en la prensa o "
    "en Wikipedia); mejor una historia famosa contada con gracia que una rara que no puedas comprobar. "
    "Extensión: entre {wmin} y {wmax} palabras. IGNORA la regla del final en bucle: termina con un remate o un "
    "último dato que cierre la historia. No saludes, no pidas seguir ni comentar, no digas 'en este vídeo'."
)


# ------------------------------------------------------------------ dibujo horizontal
def _background(ctx, sc, t, idx):
    """Solo el fondo (paisaje o color con suelo), para rellenar los laterales."""
    from src import catalog, scenery  # noqa: F401
    land = sc.get("scene") if sc.get("scene") in scenery.LANDSCAPES else None
    if land:
        scenery.draw_landscape(ctx, land, t, anim.FEET)
        return
    bg = anim.BACKGROUNDS.get(sc.get("bg"), anim.BACKGROUNDS["azul"])
    ctx.set_source_rgb(*bg)
    ctx.paint()
    ctx.rectangle(0, anim.FEET, anim.W, anim.H - anim.FEET)
    ctx.set_source_rgb(*anim.shade(bg, 0.9))
    ctx.fill()
    ctx.move_to(0, anim.FEET)
    ctx.line_to(anim.W, anim.FEET)
    ctx.set_source_rgb(*anim.shade(bg, 0.75))
    ctx.set_line_width(6)
    ctx.stroke()


def draw_wide(ctx, sc, t, dur, idx):
    for side in (-1, 1):  # laterales: el mismo paisaje en espejo, un poco oscurecido
        ctx.save()
        ctx.rectangle(CX - CW if side < 0 else CX + CW - 3, 0, CW + 3, HH)  # cada lateral solo pinta su zona
        ctx.clip()
        ctx.translate(CX if side < 0 else CX + CW, 0)
        ctx.scale(-S, S)
        ctx.translate(0 if side < 0 else -anim.W, -TOP)
        try:
            _background(ctx, sc, t, idx)
        except Exception:
            ctx.set_source_rgb(0.85, 0.9, 1)
            ctx.paint()
        ctx.restore()
    ctx.save()
    ctx.rectangle(CX, 0, CW, HH)
    ctx.clip()
    ctx.translate(CX, 0)
    ctx.scale(S, S)
    ctx.translate(0, -TOP)
    try:
        anim.draw_scene(ctx, sc, t, dur, idx)
    except Exception as e:  # red de seguridad: nunca rompe el render
        print(f"[largo] escena {idx} falló al dibujar: {e}")
        _background(ctx, sc, t, idx)
    ctx.restore()
    g = cairo.RadialGradient(WW / 2, HH / 2, HH * 0.55, WW / 2, HH / 2, WW * 0.62)  # viñeta suave en los bordes
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.28)
    ctx.set_source(g)
    ctx.paint()


def _pill(ctx, x, y, text, size, fill, fg=(1, 1, 1), anchor="left"):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(text)
    w, h = e.width + size * 1.1, size * 1.7
    if anchor == "right":
        x -= w
    r = h / 2
    ctx.new_path()
    ctx.arc(x + r, y + r, r, math.pi / 2, 1.5 * math.pi)
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    ctx.set_source_rgb(*anim.INK)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.move_to(x + (w - e.width) / 2 - e.x_bearing, y + h / 2 - e.height / 2 - e.y_bearing)
    ctx.set_source_rgb(*fg)
    ctx.show_text(text)


def _short(text, n):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def render_wide(scenes, durations, out_mp4, chapter="", num=1, total=1):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW, HH)
    ctx = cairo.Context(surf)
    tmp = out_mp4[:-4] + ".tmp.mp4"
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{WW}x{HH}", "-r", str(anim.FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", tmp],
        stdin=subprocess.PIPE)
    TR = 0.35
    T = 0.0
    try:
        for i, dur in enumerate(durations[:len(scenes)]):
            n = max(1, int(round(dur * anim.FPS)))
            for f in range(n):
                t = f / anim.FPS
                ctx.save()
                if i > 0 and t < TR:  # fundido corto entre escenas
                    draw_wide(ctx, scenes[i - 1], durations[i - 1] + t, durations[i - 1], i - 1)
                    ctx.push_group()
                    draw_wide(ctx, scenes[i], t, dur, i)
                    ctx.pop_group_to_source()
                    ctx.paint_with_alpha(anim.ease_out(t / TR))
                else:
                    draw_wide(ctx, scenes[i], t, dur, i)
                ctx.restore()
                if total > 1:
                    _pill(ctx, WW - 40, 36, f"{num}/{total}", 42, (0.2, 0.2, 0.25), anchor="right")
                if chapter and T < 4.0:  # rótulo del capítulo al empezar
                    k = anim.ease_out(min(1, T / 0.4)) * (1 if T < 3.5 else max(0, (4.0 - T) / 0.5))
                    ctx.save()
                    ctx.translate(-700 * (1 - k), 0)
                    _pill(ctx, 40, 36, _short(chapter.upper(), 44), 46, (0.95, 0.2, 0.35))
                    ctx.restore()
                surf.flush()
                proc.stdin.write(bytes(surf.get_data()))
                T += 1 / anim.FPS
    finally:
        proc.stdin.close()
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError("ffmpeg falló al renderizar el vídeo largo")
    os.replace(tmp, out_mp4)


# ------------------------------------------------------------------ guion
def _wide_subs(words, path):
    """Subtítulos para 1920x1080: abajo, sobre el suelo, algo más pequeños."""
    old = config.WIDTH, config.HEIGHT, config.FONT_SIZE
    config.WIDTH, config.HEIGHT, config.FONT_SIZE = WW, HH, 66
    try:
        subtitles.build_ass(words, path, y_frac=0.93)
    finally:
        config.WIDTH, config.HEIGHT, config.FONT_SIZE = old


def write_stories(history, theme, n):
    stories, done = [], []
    old = config.FORCE_CATEGORY, config.FORCE_NOTES, config.TARGET_WORDS
    wmin, wmax = 140, 190
    try:
        config.FORCE_CATEGORY, config.TARGET_WORDS = theme, (wmin, wmax)
        for k in range(n):
            config.FORCE_NOTES = LONG_NOTES.format(n=k + 1, total=n, theme=theme, done=", ".join(done) or "ninguna",
                                                   wmin=wmin, wmax=wmax)
            try:
                st = script_gen.generate(history + [{"topic": d, "category": theme} for d in done])
            except Exception as e:  # una historia que falla no tira el vídeo entero
                print(f"[largo] historia {k + 1} descartada: {e}")
                continue
            done.append(st.get("topic", ""))
            stories.append(st)
            print(f"[largo] historia {len(stories)}: {st.get('title')}")
    finally:
        config.FORCE_CATEGORY, config.FORCE_NOTES, config.TARGET_WORDS = old
    return stories


META_PROMPT = """Vas a publicar en YouTube un vídeo largo en {lang} sobre: {theme}.
Capítulos (en orden): {titles}
Devuelve SOLO JSON:
{{"title": "título de YouTube de máximo 70 caracteres que dé muchas ganas de verlo, con un número (ej. '10 estafas
  tan buenas que casi salen bien'), sin mentir ni exagerar lo que hay en el vídeo",
 "thumb_text": "texto de la miniatura, máximo 4 palabras, impactante",
 "description": "2-3 frases que enganchen, sin hashtags",
 "tags": ["8-12 etiquetas sin #"]}}"""


def _mmss(s):
    s = int(s)
    return f"{s // 60}:{s % 60:02d}"


# ------------------------------------------------------------------ miniatura
def thumbnail(story, text, out_png):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WW, HH)
    ctx = cairo.Context(surf)
    sc = dict(story["scenes"][0], keyword="")  # sin rótulos: el texto grande es el de la miniatura
    ctx.save()
    ctx.translate(WW * 0.2, 0)  # personaje a la derecha, texto a la izquierda
    draw_wide(ctx, sc, 1.4, 3.0, 0)
    ctx.restore()
    g = cairo.LinearGradient(0, 0, 0, HH)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.45)
    ctx.set_source(g)
    ctx.paint()
    words = str(text).upper().split()[:4]
    lines = [" ".join(words[:2]), " ".join(words[2:])] if len(words) > 2 else [" ".join(words)]
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    for li, line in enumerate(l for l in lines if l):
        size = 190
        ctx.set_font_size(size)
        while ctx.text_extents(line).width > WW * 0.42 and size > 80:
            size -= 8
            ctx.set_font_size(size)
        e = ctx.text_extents(line)
        x, y = 70, 300 + li * (size * 1.1)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.04)
        ctx.move_to(0, 0)
        ctx.text_path(line)
        ctx.set_source_rgb(*anim.INK)
        ctx.set_line_width(26)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke_preserve()
        ctx.set_source_rgb(1, 0.85, 0.15) if li == 0 else ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
        ctx.restore()
        del e
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1280, 720)
    c2 = cairo.Context(small)
    c2.scale(1280 / WW, 720 / HH)
    c2.set_source_surface(surf)
    c2.paint()
    small.write_to_png(out_png)


# ------------------------------------------------------------------ todo junto
def make(history, theme=None, n=None, demo=False):
    theme = theme or os.getenv("LONG_THEME", "").strip() or random.choice(THEMES)
    n = n or int(os.getenv("LONG_STORIES") or 10)
    work = f"{config.OUTPUT_DIR}/largo"
    os.makedirs(work, exist_ok=True)
    print(f"[largo] tema: {theme} ({n} historias)")
    if demo:
        from tests.demo import DEMO_SCRIPT
        stories = [json.loads(json.dumps(DEMO_SCRIPT)) for _ in range(n)]
        for k, s in enumerate(stories):
            s["title"] = f"Historia de prueba {k + 1}"
    else:
        stories = write_stories(history, theme, n)
    if len(stories) < 3:
        raise RuntimeError(f"Solo salieron {len(stories)} historias verificadas; no hago un vídeo largo tan corto")

    segs, chapters, t0 = [], [], 0.0
    for k, st in enumerate(stories):
        seg = f"{work}/seg{k:02d}.mp4"
        narration = " ".join(s["text"].strip() for s in st["scenes"])
        voice = f"{work}/voz{k:02d}.mp3"
        if demo:
            from tests.demo import fake_tts
            words = fake_tts(narration, voice)
        else:
            from src import tts
            words = tts.synthesize(narration, voice)
        total = render.audio_duration(voice)
        durs = render.scene_timings(st["scenes"], words, total)
        ass = f"{work}/subs{k:02d}.ass"
        _wide_subs(words, ass)
        silent = f"{work}/anim{k:02d}.mp4"
        print(f"[largo] capítulo {k + 1}/{len(stories)}: {st.get('title')} ({total:.0f} s)")
        render_wide(st["scenes"], durs, silent, chapter=st.get("title", ""), num=k + 1, total=len(stories))
        render.finish(["-i", silent], voice, ass, seg)
        chapters.append((t0, st.get("title", f"Historia {k + 1}")))
        t0 += render.audio_duration(seg)
        segs.append(seg)

    lst = f"{work}/lista.txt"
    with open(lst, "w") as f:
        f.writelines(f"file '{os.path.abspath(s)}'\n" for s in segs)
    out = f"{config.OUTPUT_DIR}/largo_{dt.datetime.now():%Y%m%d_%H%M}.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    "-movflags", "+faststart", out], check=True)

    titles = [c[1] for c in chapters]
    meta = {"title": f"{len(stories)} historias increíbles que no te contaron", "thumb_text": "NO TE LO CONTARON",
            "description": "", "tags": []}
    if not demo:
        try:
            meta.update({k: v for k, v in script_gen._chat(META_PROMPT.format(
                lang=config.LANGUAGE, theme=theme, titles="; ".join(titles)), temperature=0.9).items() if v})
        except Exception as e:
            print(f"[largo] sin título automático ({e}); uso el genérico")
    chap_txt = "\n".join(f"{_mmss(s)} {t}" for s, t in chapters)
    meta["description"] = f"{meta.get('description', '')}\n\n{chap_txt}\n\nMúsica original generada para el canal.".strip()
    thumb = f"{config.OUTPUT_DIR}/miniatura.png"
    thumbnail(stories[0], meta.get("thumb_text") or meta["title"], thumb)
    with open(f"{config.OUTPUT_DIR}/largo_info.txt", "w", encoding="utf-8") as f:
        f.write(f"{meta['title']}\n\n{meta['description']}\n\nEtiquetas: {', '.join(meta.get('tags') or [])}\n")
    print(f"[largo] listo: {out} ({t0 / 60:.1f} min)")
    return out, thumb, meta, stories, theme
