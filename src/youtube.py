"""Sube el vídeo a YouTube Shorts con la API oficial (YouTube Data API v3)."""
import json
import os

import requests

CLIENT_ID = os.getenv("YT_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "").strip()
REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "").strip()


def enabled() -> bool:
    return bool(CLIENT_ID and CLIENT_SECRET and REFRESH_TOKEN)


def _access_token() -> str:
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN, "grant_type": "refresh_token",
    }, timeout=30)
    data = r.json()
    if "access_token" not in data:
        raise RuntimeError(f"YouTube: no se pudo renovar el acceso: {data.get('error_description') or data}")
    return data["access_token"]


def upload_short(mp4: str, title: str, description: str, tags: list) -> str:
    token = _access_token()
    title = title.strip()
    if "#shorts" not in title.lower():
        title = f"{title} #shorts"
    meta = {
        "snippet": {
            "title": title[:100],
            "description": description[:4900],
            "tags": [t.lstrip("#") for t in tags][:15],
            "categoryId": "27",  # Educación
            "defaultLanguage": "es",
        },
        "status": {"privacyStatus": os.getenv("YT_PRIVACY", "public"), "selfDeclaredMadeForKids": False},
    }
    size = os.path.getsize(mp4)
    init = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(size)},
        data=json.dumps(meta), timeout=60,
    )
    if init.status_code != 200:
        raise RuntimeError(f"YouTube: error al iniciar la subida ({init.status_code}): {init.text[:300]}")
    with open(mp4, "rb") as f:
        up = requests.put(init.headers["Location"], data=f,
                          headers={"Authorization": f"Bearer {token}", "Content-Type": "video/mp4"}, timeout=600)
    if up.status_code not in (200, 201):
        raise RuntimeError(f"YouTube: error al subir ({up.status_code}): {up.text[:300]}")
    vid = up.json()["id"]
    status = up.json().get("status", {}).get("privacyStatus")
    print(f"[youtube] publicado: https://youtube.com/shorts/{vid} ({status})")
    return vid
