"""Vídeo largo horizontal para YouTube (~8-10 min, varias historias con capítulos).

Uso:
  python largo.py               # genera y, si PUBLISH=true, lo sube a YouTube
  python largo.py --no-publish  # solo genera (vídeo + miniatura + texto en output/)
  python largo.py --demo        # prueba offline con 3 historias falsas
Variables opcionales: LONG_THEME (tema), LONG_STORIES (nº de historias, 10), LONG_PRIVACY (public/unlisted/private)
"""
import argparse
import datetime as dt
import os
import sys

import config
from main import load_history, save_history


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    history = load_history()

    from src import longform, notify
    out, thumb, meta, stories, theme = longform.make(history, n=3 if args.demo else None, demo=args.demo)

    entry = {"date": dt.date.today().isoformat(), "category": theme, "format": "largo", "series": None,
             "topic": "vídeo largo: " + "; ".join(s.get("topic", "") for s in stories), "title": meta["title"]}
    publish = not args.no_publish and not args.demo and os.getenv("PUBLISH", "false").lower() == "true"
    errors = []
    if publish:
        from src import youtube
        vid = youtube.upload_video(out, meta["title"], meta["description"], meta.get("tags") or [], short=False,
                                   privacy=os.getenv("LONG_PRIVACY") or None)
        entry["youtube_id"] = vid
        try:
            youtube.set_thumbnail(vid, thumb)
        except Exception as e:
            errors.append(f"Miniatura: {e} (verifica el canal con tu teléfono en youtube.com/verify para poder ponerla)")
    if not args.demo:
        # cada historia queda en el historial para que los Shorts no las repitan
        history += [{"date": entry["date"], "category": theme, "format": "largo-capitulo", "topic": s.get("topic", ""),
                     "title": s.get("title", "")} for s in stories]
        history.append(entry)
        save_history(history)
        mins = longform.render.audio_duration(out) / 60
        lines = [f"🎬 **Vídeo largo** ({mins:.1f} min, {len(stories)} historias) — {meta['title']}"]
        if entry.get("youtube_id"):
            lines.append(f"▶️ https://youtube.com/watch?v={entry['youtube_id']}")
        else:
            lines.append("Sin publicar: descárgalo del artifact de GitHub para revisarlo.")
        lines += [f"⚠️ {e}" for e in errors]
        notify.message("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        from src import notify
        notify.failed(f"Vídeo largo: {type(e).__name__}: {e}")
        raise
