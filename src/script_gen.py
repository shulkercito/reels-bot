"""Genera el guion del vídeo con un LLM gratuito (Gemini o Groq)."""
import json
import random
import re
import time

import requests

import config

FALLBACK_GEMINI = ["gemini-3.8-flash", "gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-3.1-flash-lite"]

PROMPT = """Eres guionista de vídeos virales cortos (Reels/TikTok) de {category}.
Escribe UN vídeo en idioma "{lang}" sobre un tema concreto y verídico dentro de esa categoría.

Reglas:
- Primera frase = gancho brutal de menos de 12 palabras que obligue a quedarse (pregunta o afirmación chocante).
- Narración total entre {wmin} y {wmax} palabras, frases cortas, tono de contar un secreto, sin emojis.
- Solo hechos reales y comprobables; si hay incertidumbre, dilo ("se cree que...").
- Termina con una frase que invite a comentar o seguir la cuenta, sin ser pesado.
- Divide la narración en 10 a 14 escenas cortas (una frase o media frase cada una). El texto de las escenas, unido, es la narración completa.
- Para cada escena, un prompt de imagen EN INGLÉS que muestre PERSONAJES haciendo algo: quién aparece, qué acción exagerada hace,
  qué expresión tiene (sorpresa, miedo, risa...) y dónde está. Estilo visual del vídeo: {style_hint}.
  Una sola escena clara por imagen, sin texto, sin letras, sin famosos reales reconocibles, sin marcas.
- NO repitas ninguno de estos temas ya publicados: {history}

Devuelve SOLO JSON válido con esta forma:
{{
  "topic": "tema concreto en pocas palabras",
  "title": "título corto",
  "scenes": [{{"text": "frase(s) de la narración", "image_prompt": "english visual prompt"}}],
  "caption": "descripción para Instagram de 1-2 frases con gancho",
  "hashtags": ["#...", "..."]
}}"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1])


def pick_category(history: list) -> str:
    last = history[-1]["category"] if history else None
    options = [c for c in config.CATEGORIES if c != last]
    return random.choice(options)


def pick_style(history: list) -> str:
    """VISUAL_STYLE=mix alterna estilos; si no, usa el elegido."""
    if config.VISUAL_STYLE in config.VISUAL_STYLES:
        return config.VISUAL_STYLE
    last = history[-1].get("style") if history else None
    options = [s for s in config.VISUAL_STYLES if s != last] or list(config.VISUAL_STYLES)
    return random.choice(options)


def generate(history: list) -> dict:
    if not config.LLM_API_KEY:
        raise RuntimeError("Falta LLM_API_KEY")
    category = pick_category(history)
    style = pick_style(history)
    used = ", ".join(h["topic"] for h in history[-80:]) or "ninguno"
    prompt = PROMPT.format(
        category=category, lang=config.LANGUAGE, history=used,
        style_hint=config.VISUAL_STYLES[style]["hint"],
        wmin=config.TARGET_WORDS[0], wmax=config.TARGET_WORDS[1],
    )
    # Si un modelo está saturado (503/429) o no existe (404), prueba el siguiente.
    models = [config.LLM_MODEL]
    if config.LLM_PROVIDER == "gemini":
        models += [m for m in FALLBACK_GEMINI if m != config.LLM_MODEL]

    last_err = None
    for model in models:
        for attempt in range(3):
            try:
                r = requests.post(
                    f"{config.LLM_BASE_URL}/chat/completions",
                    headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 1.0,
                        "response_format": {"type": "json_object"},
                    },
                    timeout=180,
                )
                if r.status_code == 404:
                    raise LookupError(f"modelo {model} no disponible")
                if r.status_code in (429, 500, 502, 503, 504):
                    raise ConnectionError(f"{r.status_code} servidor saturado: {r.text[:150]}")
                r.raise_for_status()
                data = _extract_json(r.json()["choices"][0]["message"]["content"])
                _validate(data)
                data["category"] = category
                data["style"] = style
                print(f"[guion] generado con {model} (estilo {style})")
                return data
            except LookupError as e:
                last_err = e
                print(f"[guion] {e}, paso al siguiente modelo")
                break
            except Exception as e:
                last_err = e
                wait = 15 * (attempt + 1)
                print(f"[guion] {model} intento {attempt + 1} falló: {e} — espero {wait}s")
                time.sleep(wait)
    raise RuntimeError(f"No se pudo generar el guion: {last_err}")


def _validate(data: dict):
    scenes = data.get("scenes") or []
    if len(scenes) < 6:
        raise ValueError("muy pocas escenas")
    words = sum(len(s["text"].split()) for s in scenes)
    if words < 70 or words > 220:
        raise ValueError(f"longitud rara: {words} palabras")
    for s in scenes:
        if not s.get("text") or not s.get("image_prompt"):
            raise ValueError("escena incompleta")
