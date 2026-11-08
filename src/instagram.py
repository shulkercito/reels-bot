"""Publica el vídeo como Reel con la API oficial de Instagram (cuenta profesional)."""
import os
import time

import requests

import config


def _check(r: requests.Response) -> dict:
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Instagram: {data['error'].get('message')}")
    return data


def _token() -> str:
    # quita espacios, saltos de línea y comillas que se cuelan al pegar
    return "".join(config.IG_ACCESS_TOKEN.split()).strip("\"'")


def _api_base(token: str) -> str:
    """Los tokens de Instagram (IG...) van a graph.instagram.com; los de Facebook (EAA...) a graph.facebook.com."""
    version = config.IG_API.rstrip("/").split("/")[-1]
    if token.startswith("EAA"):
        return f"https://graph.facebook.com/{version}"
    return config.IG_API


def describe_token() -> str:
    t = _token()
    kind = "Facebook (EAA)" if t.startswith("EAA") else "Instagram (IG)" if t.startswith("IG") else "desconocido"
    return f"token tipo {kind}, {len(t)} caracteres, empieza por '{t[:4]}', termina por '{t[-3:]}'"


def refresh_token() -> str:
    """Alarga el token de larga duración otros 60 días. Devuelve el token nuevo."""
    token = _token()
    if token.startswith("EAA"):
        raise RuntimeError("los tokens de Facebook no se renuevan así; se omite la renovación")
    r = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token},
        timeout=30,
    )
    return _check(r)["access_token"]


def publish_reel(video_url: str, caption: str) -> str:
    """video_url tiene que ser un enlace público y directo al .mp4."""
    if not (config.IG_USER_ID and config.IG_ACCESS_TOKEN):
        raise RuntimeError("Faltan IG_USER_ID o IG_ACCESS_TOKEN")
    token = _token()
    base = _api_base(token)
    print(f"[instagram] {describe_token()} -> {base}")

    container = _check(requests.post(
        f"{base}/{config.IG_USER_ID}/media",
        data={"media_type": "REELS", "video_url": video_url, "caption": caption,
              "share_to_feed": "true", "access_token": token},
        timeout=60,
    ))["id"]
    print(f"[instagram] contenedor {container} creado, esperando procesado…")
    return _wait_and_publish(base, token, container)


def publish_reel_file(mp4: str, caption: str) -> str:
    """Sube el archivo directamente a Meta (sin enlaces). Requiere token de Facebook (EAA...)."""
    if not (config.IG_USER_ID and config.IG_ACCESS_TOKEN):
        raise RuntimeError("Faltan IG_USER_ID o IG_ACCESS_TOKEN")
    token = _token()
    if not token.startswith("EAA"):
        raise RuntimeError("la subida directa solo funciona con tokens de Facebook (EAA)")
    base = _api_base(token)
    version = base.rstrip("/").split("/")[-1]
    print(f"[instagram] {describe_token()} -> subida directa del archivo")
    created = _check(requests.post(
        f"{base}/{config.IG_USER_ID}/media",
        params={"upload_type": "resumable"},
        headers={"Authorization": f"Bearer {token}"},
        json={"media_type": "REELS", "caption": caption, "share_to_feed": True},
        timeout=60,
    ))
    container = created["id"]
    upload_uri = created.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{version}/{container}"
    size = os.path.getsize(mp4)
    with open(mp4, "rb") as f:
        up = requests.post(upload_uri, data=f, timeout=600, headers={
            "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)})
    try:
        body = up.json()
    except ValueError:
        body = {"raw": up.text[:300]}
    if up.status_code != 200 or not body.get("success"):
        raise RuntimeError(f"subida directa falló ({up.status_code}): {body}")
    print(f"[instagram] archivo subido ({size // 1024} KB), contenedor {container}, esperando procesado…")
    return _wait_and_publish(base, token, container)


def _wait_and_publish(base: str, token: str, container: str) -> str:
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
