"""Publica el vídeo como Reel con la API oficial de Instagram (cuenta profesional)."""
import time

import requests

import config


def _check(r: requests.Response) -> dict:
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Instagram: {data['error'].get('message')}")
    return data


def refresh_token() -> str:
    """Alarga el token de larga duración otros 60 días. Devuelve el token nuevo."""
    r = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": config.IG_ACCESS_TOKEN},
        timeout=30,
    )
    return _check(r)["access_token"]


def publish_reel(video_url: str, caption: str) -> str:
    """video_url tiene que ser un enlace público y directo al .mp4."""
    if not (config.IG_USER_ID and config.IG_ACCESS_TOKEN):
        raise RuntimeError("Faltan IG_USER_ID o IG_ACCESS_TOKEN")
    base, token = config.IG_API, config.IG_ACCESS_TOKEN

    container = _check(requests.post(
        f"{base}/{config.IG_USER_ID}/media",
        data={"media_type": "REELS", "video_url": video_url, "caption": caption,
              "share_to_feed": "true", "access_token": token},
        timeout=60,
    ))["id"]
    print(f"[instagram] contenedor {container} creado, esperando procesado…")

    for _ in range(60):  # hasta ~10 min
        status = _check(requests.get(
            f"{base}/{container}", params={"fields": "status_code,status", "access_token": token}, timeout=30,
        ))
        code = status.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram no pudo procesar el vídeo: {status}")
        time.sleep(10)
    else:
        raise RuntimeError("Instagram tardó demasiado en procesar el vídeo")

    media_id = _check(requests.post(
        f"{base}/{config.IG_USER_ID}/media_publish",
        data={"creation_id": container, "access_token": token}, timeout=60,
    ))["id"]
    print(f"[instagram] publicado: media {media_id}")
    return media_id
