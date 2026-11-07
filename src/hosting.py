"""Instagram necesita el vídeo en una URL pública. Dos opciones gratis."""
import os

import requests


def via_github_release(mp4: str, tag: str) -> str:
    """Sube el mp4 como asset de una release del repo (el repo debe ser público)."""
    repo, token = os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"]
    h = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    rel = requests.post(f"https://api.github.com/repos/{repo}/releases", headers=h,
                        json={"tag_name": tag, "name": tag, "body": "Reel generado automáticamente"}, timeout=30)
    rel.raise_for_status()
    upload_url = rel.json()["upload_url"].split("{")[0]
    with open(mp4, "rb") as f:
        asset = requests.post(upload_url, params={"name": os.path.basename(mp4)},
                              headers={**h, "Content-Type": "video/mp4"}, data=f, timeout=300)
    asset.raise_for_status()
    return asset.json()["browser_download_url"]


def via_catbox(mp4: str) -> str:
    """Alternativa sin cuenta: catbox.moe (enlace directo .mp4)."""
    with open(mp4, "rb") as f:
        r = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"},
                          files={"fileToUpload": f}, timeout=300)
    r.raise_for_status()
    if not r.text.startswith("https://"):
        raise RuntimeError(f"catbox: {r.text[:200]}")
    return r.text.strip()


def upload(mp4: str, tag: str) -> str:
    method = os.getenv("VIDEO_HOST", "github")
    return via_catbox(mp4) if method == "catbox" else via_github_release(mp4, tag)
