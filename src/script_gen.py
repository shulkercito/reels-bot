"""Genera el guion del vídeo con un LLM gratuito (Gemini o Groq)."""
import json
import random
import re

import requests

import config

PROMPT = """Eres guionista de vídeos virales cortos (Reels/TikTok) de {category}.
Escribe UN vídeo en idioma "{lang}" sobre un tema concreto y verídico dentro de esa categoría.

Reglas:
- Primera frase = gancho brutal de menos de 12 palabras que obligue a quedarse (pregunta o afirmación chocante).
- Narración total entre {wmin} y {wmax} palabras, frases cortas, tono de contar un secreto, sin emojis.
- Solo hechos reales y comprobables; si hay incertidumbre, dilo ("se cree que...").
- Termina con una frase que invite a comentar o seguir la cuenta, sin ser pesado.
- Divide la narración en 6 a 9 escenas. El texto de las escenas, unido, es la narración completa.
- Para cada escena, un prompt de imagen EN INGLÉS, visual y concreto (sin texto en la imagen, sin personas reales famosas reconocibles, sin marcas).
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


def generate(history: list) -> dict:
    if not config.LLM_API_KEY:
        raise RuntimeError("Falta LLM_API_KEY")
    category = pick_category(history)
    used = ", ".join(h["topic"] for h in history[-80:]) or "ninguno"
    prompt = PROMPT.format(
        category=category, lang=config.LANGUAGE, history=used,
        wmin=config.TARGET_WORDS[0], wmax=config.TARGET_WORDS[1],
    )
    last_err = None
    for attempt in range(3):
        r = requests.post(
            f"{config.LLM_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
            json={
                "model": config.LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 1.0,
                "response_format": {"type": "json_object"},
            },
            timeout=120,
        )
        try:
            r.raise_for_status()
            data = _extract_json(r.json()["choices"][0]["message"]["content"])
            _validate(data)
            data["category"] = category
            return data
        except Exception as e:  # reintenta si el JSON sale mal
            last_err = e
            print(f"[guion] intento {attempt + 1} falló: {e}")
    raise RuntimeError(f"No se pudo generar el guion: {last_err}")


def _validate(data: dict):
    scenes = data.get("scenes") or []
    if len(scenes) < 4:
        raise ValueError("muy pocas escenas")
    words = sum(len(s["text"].split()) for s in scenes)
    if words < 70 or words > 220:
        raise ValueError(f"longitud rara: {words} palabras")
    for s in scenes:
        if not s.get("text") or not s.get("image_prompt"):
            raise ValueError("escena incompleta")
