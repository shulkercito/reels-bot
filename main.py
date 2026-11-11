"""Bot de Reels de curiosidades: guion -> voz -> imágenes -> montaje -> Instagram.

Uso:
  python main.py              # genera el vídeo y lo publica (si PUBLISH=true)
  python main.py --no-publish # solo genera el vídeo en output/
  python main.py --demo       # prueba offline del montaje, sin APIs
"""
import argparse
import datetime as dt
import json
import os
import sys
import time

import config
from src import render, subtitles


def load_history() -> list:
    if os.path.exists(config.HISTORY_FILE):
        with open(config.HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history: list):
    with open(config.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def build_caption(script: dict) -> str:
    tags = " ".join(t if t.startswith("#") else f"#{t}" for t in script.get("hashtags", [])[:12])
    head = f"{script['series_label']} · " if script.get("series_label") else ""
    return f"{head}{script['caption']}\n\n{tags}".strip()


def assign_series(script: dict, history: list):
    """Cada temática es una serie fija con su número de episodio ("Mitos falsos #12")."""
    name = config.SERIES.get(script.get("category", ""))
    if not name:
        return
    # solo cuentan los vídeos que llegaron a publicarse (las pruebas no gastan número)
    ep = 1 + sum(1 for h in history if h.get("series") == name and (h.get("instagram_id") or h.get("youtube_id")))
    script["series"], script["episode"] = name, ep
    script["series_label"] = f"{name} #{ep}"


def make_video(script: dict, work: str, demo=False) -> str:
    narration = " ".join(s["text"].strip() for s in script["scenes"])
    voice = f"{work}/voice.mp3"

    style = script.get("style", config.VISUAL_STYLE)
    animated = style == "animado"

    if demo:
        from tests.demo import fake_tts, fake_images
        words = fake_tts(narration, voice)
        images = None if animated else fake_images(len(script["scenes"]), work)
    else:
        from src import tts
        print("[voz] sintetizando…")
        words = tts.synthesize(narration, voice)
        images = None
        if not animated:
            from src import images as img_mod
            print("[imágenes] generando…")
            images = img_mod.generate([s["image_prompt"] for s in script["scenes"]], work, style=style)

    total = render.audio_duration(voice)
    durations = render.scene_timings(script["scenes"], words, total)
    ass = f"{work}/subs.ass"
    # en la animación los subtítulos van abajo, debajo de los personajes
    subtitles.build_ass(words, ass, y_frac=0.745 if animated else 0.62)

    out = f"{config.OUTPUT_DIR}/reel_{dt.datetime.now():%Y%m%d_%H%M}.mp4"
    print(f"[montaje] {len(script['scenes'])} escenas, {total:.1f} s, estilo {style}…")
    if animated:
        render.render_animated(script["scenes"], durations, voice, ass, out, work,
                               hook=script.get("hook_title", ""), series=(script.get("series_label") or "").upper())
    else:
        render.render(images, durations, voice, ass, out, work, style=style)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    work = f"{config.OUTPUT_DIR}/work"
    os.makedirs(work, exist_ok=True)
    history = load_history()

    if args.demo:
        from tests.demo import DEMO_SCRIPT as script
    else:
        from src import script_gen
        print("[guion] generando…")
        script = script_gen.generate(history)
    print(f"[guion] {script['category']} -> {script['topic']}")

    assign_series(script, history)
    mp4 = make_video(script, work, demo=args.demo)
    caption = build_caption(script)
    with open(f"{config.OUTPUT_DIR}/caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
    print(f"[ok] vídeo: {mp4}")

    entry = {"date": dt.date.today().isoformat(), "category": script["category"],
             "style": script.get("style"), "series": script.get("series"), "episode": script.get("episode"),
             "hook": script.get("hook_title"),
             "topic": script["topic"], "title": script["title"]}

    publish = not args.no_publish and not args.demo and os.getenv("PUBLISH", "false").lower() == "true"
    errors = []
    if publish:
        from src import youtube
        # cada red va por separado: si una falla, la otra se publica igual
        if os.getenv("IG_ACCESS_TOKEN"):
            from src import hosting, instagram
            tag = f"reel-{dt.datetime.now():%Y%m%d-%H%M%S}"
            # 1º subida directa del archivo; si Instagram no lo procesa, se reexporta con
            # ajustes "ultra seguros" y se reintenta (directa y por enlace)
            attempts = [("directa", "original"), ("directa", "seguro"), ("github", "seguro")]
            safe_mp4 = None
            last_err = None
            for n, (how, version) in enumerate(attempts):
                try:
                    f = mp4
                    if version == "seguro":
                        if safe_mp4 is None:
                            safe_mp4 = render.safe_copy(mp4)
                            print(f"[instagram] reexportado en modo seguro: {safe_mp4}")
                        f = safe_mp4
                    if how == "directa":
                        entry["instagram_id"] = instagram.publish_reel_file(f, caption)
                    else:
                        url = hosting.via_github_release(f, f"{tag}-{n}")
                        print(f"[hosting] {url}")
                        entry["instagram_id"] = instagram.publish_reel(url, caption)
                    print(f"[instagram] OK con el vídeo {version}")
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    print(f"[instagram] intento {n + 1} ({how}, vídeo {version}) falló: {e}")
                    time.sleep(20)
            if last_err:
                errors.append(f"Instagram: {last_err}")
                print(f"[instagram] ERROR: {last_err}")
        if youtube.enabled():
            try:
                entry["youtube_id"] = youtube.upload_short(mp4, script["title"], caption, script.get("hashtags", []))
            except Exception as e:
                errors.append(f"YouTube: {e}")
                print(f"[youtube] ERROR: {e}")
        else:
            print("[youtube] sin configurar (faltan YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN)")
    else:
        print("[publicar] desactivado (PUBLISH!=true): el vídeo queda en output/")

    if not args.demo:
        history.append(entry)
        save_history(history)

    from src import notify
    if publish:
        notify.published(script, mp4, entry, errors)  # te llega el vídeo con los enlaces (y avisos si algo falló)
    elif not args.demo:
        notify.generated(script, mp4)
    if errors:  # la ejecución sale en rojo para que te enteres
        raise AlreadyNotified(" | ".join(errors))


class AlreadyNotified(RuntimeError):
    """Error que ya se ha avisado al móvil junto con el vídeo."""


if __name__ == "__main__":
    try:
        main()
    except AlreadyNotified as e:
        print(f"[error] {e}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        from src import notify
        notify.failed(f"{type(e).__name__}: {e}")
        raise
