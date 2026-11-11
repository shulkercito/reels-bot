"""Avisos al móvil por Discord (webhook) y/o Telegram: vídeo publicado (con el vídeo) o error."""
import json
import os

import requests

DISCORD = os.getenv("DISCORD_WEBHOOK", "").strip()
TG_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
TG_CHAT = os.getenv("TELEGRAM_CHAT_ID", "").strip()
DISCORD_MAX = 9.5 * 1024 * 1024   # límite de archivos por webhook en servidores normales (10 MB)
TELEGRAM_MAX = 49 * 1024 * 1024


def enabled() -> bool:
    return bool(DISCORD or (TG_TOKEN and TG_CHAT))


def run_url() -> str:
    if os.getenv("GITHUB_RUN_ID"):
        return (f"{os.getenv('GITHUB_SERVER_URL', 'https://github.com')}/{os.getenv('GITHUB_REPOSITORY')}"
                f"/actions/runs/{os.getenv('GITHUB_RUN_ID')}")
    return ""


def _post(url, **kw):
    try:
        r = requests.post(url, timeout=120, **kw)
        if not r.ok:
            print(f"[aviso] falló ({r.status_code}): {r.text[:200]}")
        return r
    except requests.RequestException as e:  # un aviso nunca debe romper la publicación
        print(f"[aviso] error de red: {e}")
        return None


def message(text: str):
    if DISCORD:
        _post(DISCORD, json={"content": text[:1990]})
    if TG_TOKEN and TG_CHAT:
        _post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
              data={"chat_id": TG_CHAT, "text": text.replace("**", "")[:4000], "disable_web_page_preview": "true"})


def video(path: str, text: str):
    size = os.path.getsize(path) if os.path.exists(path) else 0
    if DISCORD:
        sent = False
        if 0 < size < DISCORD_MAX:
            with open(path, "rb") as f:
                r = _post(DISCORD, data={"payload_json": json.dumps({"content": text[:1990]})},
                          files={"file": (os.path.basename(path), f, "video/mp4")})
            sent = r is not None and r.ok
        if not sent:
            _post(DISCORD, json={"content": (text + "\n(vídeo demasiado grande para adjuntarlo)")[:1990]})
    if TG_TOKEN and TG_CHAT:
        sent = False
        if 0 < size < TELEGRAM_MAX:
            with open(path, "rb") as f:
                r = _post(f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo",
                          data={"chat_id": TG_CHAT, "caption": text.replace("**", "")[:1000], "supports_streaming": "true"},
                          files={"video": f})
            sent = r is not None and r.ok
        if not sent:
            message(text)


def published(script: dict, mp4: str, entry: dict, errors: list):
    lines = [f"✅ **{script.get('series_label') or 'Nuevo vídeo'}** — {script.get('title', '')}"]
    if entry.get("youtube_id"):
        lines.append(f"▶️ YouTube: https://youtube.com/shorts/{entry['youtube_id']}")
    if entry.get("instagram_id"):
        lines.append("📸 Instagram: publicado")
    for e in errors:
        lines.append(f"⚠️ {str(e)[:300]}")
    if run_url():
        lines.append(f"🔧 <{run_url()}>")
    video(mp4, "\n".join(lines))


def generated(script: dict, mp4: str):
    """Vídeo generado sin publicar (prueba): te llega para revisarlo."""
    video(mp4, f"🎬 **Prueba sin publicar** — {script.get('series_label') or ''} {script.get('title', '')}")


def failed(err: str):
    txt = f"❌ **El bot de Reels ha fallado**\n```\n{str(err)[:1500]}\n```"
    if run_url():
        txt += f"\n🔧 <{run_url()}>"
    message(txt)
