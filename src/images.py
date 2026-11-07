"""Imágenes gratis con Pollinations (modelo FLUX)."""
import random
import time
import urllib.parse

import requests

import config


def _download(prompt: str, path: str, seed: int) -> bool:
    full = f"{prompt}, {config.IMAGE_STYLE}"
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(full)
    params = {
        "width": config.WIDTH, "height": config.HEIGHT, "model": config.IMAGE_MODEL,
        "seed": seed, "nologo": "true", "enhance": "false",
    }
    headers = {"Authorization": f"Bearer {config.POLLINATIONS_TOKEN}"} if config.POLLINATIONS_TOKEN else {}
    r = requests.get(url, params=params, headers=headers, timeout=180)
    if r.ok and r.headers.get("content-type", "").startswith("image") and len(r.content) > 20_000:
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    print(f"[imagen] fallo {r.status_code}: {r.text[:120]!r}")
    return False


def generate(prompts: list, out_dir: str) -> list:
    paths, ok_any = [], None
    for i, prompt in enumerate(prompts):
        path = f"{out_dir}/scene_{i:02d}.jpg"
        done = False
        for attempt in range(4):
            try:
                if _download(prompt, path, random.randint(1, 10**6)):
                    done = True
                    break
            except requests.RequestException as e:
                print(f"[imagen] error de red: {e}")
            time.sleep(6 * (attempt + 1))  # respeta la cuota gratuita
        if done:
            ok_any = path
            paths.append(path)
        elif ok_any:
            print(f"[imagen] escena {i} reutiliza la anterior")
            paths.append(ok_any)
        else:
            paths.append(None)
    # rellena huecos del principio con la primera imagen buena
    first = next((p for p in paths if p), None)
    if not first:
        raise RuntimeError("No se pudo generar ninguna imagen")
    return [p or first for p in paths]
