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
- GANCHO: escribe 3 ganchos MUY distintos (pregunta intrigante, afirmación chocante, "no te vas a creer...") y elige
  el más potente. El elegido es la PRIMERA frase de la narración (menos de 12 palabras) y además su versión corta va
  en pantalla desde el primer segundo ("hook_title", máximo 6 palabras, que dé ganas de quedarse).
- Narración total entre {wmin} y {wmax} palabras, frases cortas, sin emojis.
- Tono ENTRETENIDO y cercano, como un colega contándote un cotilleo increíble: con giros, humor y sorpresa.
  NO es una clase de ciencias: nada de tecnicismos ni explicaciones de libro si el tema no lo pide.
  Si es una historia, cuéntala como una historia (personajes, qué pasó, giro final).
- Solo hechos reales y comprobables; si hay incertidumbre, dilo ("se cree que...").
- Termina con una frase que invite a comentar o seguir la cuenta, sin ser pesado.
- Divide la narración en 10 a 14 escenas cortas (una frase o media frase cada una). El texto de las escenas, unido, es la narración completa.
{scene_rules}
- NO repitas ninguno de estos temas ya publicados: {history}

Devuelve SOLO JSON válido con esta forma:
{{
  "topic": "tema concreto en pocas palabras",
  "title": "título corto",
  "hooks": ["gancho 1", "gancho 2", "gancho 3"],
  "hook_title": "texto corto en pantalla (máx. 6 palabras)",
  "scenes": [{scene_schema}],
  "caption": "descripción para Instagram de 1-2 frases con gancho",
  "hashtags": ["#...", "..."]
}}"""

IMAGE_RULES = """- Para cada escena, un prompt de imagen EN INGLÉS que muestre PERSONAJES haciendo algo: quién aparece, qué acción exagerada hace,
  qué expresión tiene (sorpresa, miedo, risa...) y dónde está. Estilo visual del vídeo: {style_hint}.
  Una sola escena clara por imagen, sin texto, sin letras, sin famosos reales reconocibles, sin marcas."""
IMAGE_SCHEMA = '{{"text": "frase(s) de la narración", "image_prompt": "english visual prompt"}}'

ANIM_RULES = """- El vídeo es una ANIMACIÓN de monigotes. Para cada escena elige cómo se anima, SOLO con estos valores:
  * "action" (lo que hace el monigote protagonista): {actions}
  * "props" (0 a 3 objetos pequeños que aparecen; pueden repetirse, ej. 3 corazones): {props}
    o CUALQUIER nombre de la lista de iconos de abajo (ej. "syringe", "violin", "coin").
  * "keyword": 1-3 palabras en MAYÚSCULAS que resumen la escena (un número, un dato clave) o "" si no hace falta.
    Pon keyword en más o menos la mitad de las escenas, no en todas.
  * "second": acción de un segundo monigote que reacciona (de la misma lista de acciones) o "" si está solo. Úsalo en 2-4 escenas.
  * "scene": PAISAJE de fondo animado que sitúa la historia: {scenes}.
    Elige el que encaje con lo que se cuenta (un pulpo -> mar o abismo, un faraón -> egipto, un planeta -> espacio,
    un récord deportivo -> estadio, un experimento -> laboratorio...). Puede repetirse en escenas seguidas del mismo
    lugar y cambiar cuando cambie el lugar. "" = fondo de color liso (para escenas de "idea", datos o gráficas).
  * "bg": color de fondo liso cuando "scene" es "": {bgs}.
  * "creature": si se habla de algo de este catálogo, ponlo y aparecerá ANIMADO junto al monigote.
{creatures}
    (human = cuerpo humano genérico). Úsalo en TODAS las escenas donde encaje; elige el más concreto posible.
    "" si no aplica.
  * "custom": si lo que se nombra es un ANIMAL o un PERSONAJE concreto que NO está en el catálogo (un ornitorrinco,
    Napoleón, Cleopatra, un gladiador, una llama...), diséñalo tú con una plantilla y pon "creature": "custom".
    Cuanto más fiel, mejor (colores reales, ropa y objetos típicos de la época). Formatos:
{custom_help}
    Repite EXACTAMENTE el mismo "custom" en todas las escenas donde salga el mismo personaje.
  * "icon": si lo que se nombra es un OBJETO, lugar, comida, vehículo, planta o símbolo concreto que no está en el
    catálogo, elige su icono EXACTO de esta lista (se anima junto al monigote). Úsalo también para concretar
    mucho: una vacuna, un violín, un volcán, un sushi, una brújula... "" si no aplica.
    Iconos: {icons}
  * Orden de preferencia para que el vídeo NUNCA quede genérico: "creature" del catálogo > "custom" > "icon".
    Casi todas las escenas deberían mostrar algo concreto de lo que se está contando.
  * "xray": true cuando la escena explica lo que hay DENTRO de la criatura (órganos, corazón, huesos, capas
    de la Tierra, magma del volcán, cámaras de la pirámide...): se verá por dentro con efecto rayos X. Si no, false.
  * "zoom": SOLO si la escena explica cómo funciona algo por dentro (cuerpo, naturaleza, ciencia, máquinas). En historias,
    deporte, famosos, cine, comida, etc. normalmente NO hace falta: usa personajes, escenarios e iconos. Cuando la escena cuente CÓMO FUNCIONA algo o QUÉ
    PASA por dentro, aparece una lupa que muestra ese proceso animado. Formato:
    {{"of": parte de la criatura de donde sale la lupa ({parts}) o "", "items": 1 a 4 elementos}}
    cada elemento: {{"kind": tipo, "label": "NOMBRE CORTO EN ESPAÑOL", "do": qué hace, "color": opcional ({colors})}}
    tipos y lo que pueden hacer: {kinds}
    Ejemplo (el cerebro se limpia al dormir): {{"of": "brain", "items": [{{"kind": "cells", "label": "NEURONAS", "do": "shrink"}},
    {{"kind": "fluid", "label": "LÍQUIDO", "do": "flow"}}, {{"kind": "particles", "label": "RESIDUOS", "do": "exit"}}]}}
    Ejemplo (fisión nuclear): {{"of": "", "items": [{{"kind": "atoms", "label": "URANIO", "do": "split"}}]}}
    Ejemplo (las defensas atacan un virus): {{"of": "", "items": [{{"kind": "blood", "label": "SANGRE", "do": "flow"}}, {{"kind": "virus", "label": "VIRUS", "do": "die"}}]}}
    Úsalo en 0-3 escenas según el tema. Con zoom, la criatura puede ir en rayos X ("xray": true). null si no.
    "xray" igual: solo cuando de verdad aporte (ver huesos, órganos, el interior de algo).
  * "chart": cuando la escena da CIFRAS, una gráfica animada (nunca en la misma escena que "zoom"):
    comparación -> {{"type": "bars", "title": "...", "unit": "kg", "items": [{{"label": "Humano", "value": 1.4}}, {{"label": "Elefante", "value": 4.8}}]}}
    un número impactante -> {{"type": "counter", "to": 86000000000, "prefix": "", "suffix": "", "title": "neuronas en tu cerebro"}}
    Solo cifras reales; values como números. Úsalo en 1-2 escenas si hay datos. null si no.
  * Si el tema NO está en el catálogo, no inventes criaturas: cuéntalo con los monigotes, el segundo monigote
    y los "props" (objetos) que mejor lo representen.
- Varía mucho las acciones: que no se repita la misma acción en dos escenas seguidas.
  Usa "shocked" en el gancho, "point" cuando se explica un objeto, "think" ante preguntas, "celebrate"/"laugh" en el final."""
ANIM_SCHEMA = ('{{"text": "frase(s) de la narración", "action": "...", "props": ["..."], '
               '"keyword": "...", "second": "...", "scene": "...", "bg": "...", "creature": "...", "custom": null, "icon": "...", "xray": false, "zoom": null, "chart": null}}')


def _extract_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1])


def pick_category(history: list) -> str:
    """Elige una temática que no haya salido en los últimos vídeos (máxima variedad)."""
    recent = {h.get("category") for h in history[-8:]}
    options = [c for c in config.CATEGORIES if c not in recent] or config.CATEGORIES
    return random.choice(options)


def pick_style(history: list) -> str:
    """VISUAL_STYLE=mix alterna estilos; si no, usa el elegido."""
    if config.VISUAL_STYLE in config.VISUAL_STYLES:
        return config.VISUAL_STYLE
    image_styles = [s for s in config.VISUAL_STYLES if s != "animado"]
    last = history[-1].get("style") if history else None
    options = [s for s in image_styles if s != last] or image_styles
    return random.choice(options)


def generate(history: list) -> dict:
    if not config.LLM_API_KEY:
        raise RuntimeError("Falta LLM_API_KEY")
    category = pick_category(history)
    style = pick_style(history)
    used = ", ".join(h["topic"] for h in history[-80:]) or "ninguno"
    if style == "animado":
        from src import anim
        from src import catalog, creatures, custom, emoji, explain, scenery
        parts = sorted({p for d in creatures.PARTS.values() for p in d})
        cat_txt = "\n".join(f"    - {g}: {', '.join(n)}" for g, n in catalog.GROUPS.items())
        kinds = "; ".join(f"{k} ({'/'.join(v)})" for k, v in explain.DOS.items())
        rules = ANIM_RULES.format(actions=", ".join(anim.ACTIONS), props=", ".join(anim.PROPS),
                                  bgs=", ".join(anim.BACKGROUNDS), creatures=cat_txt, scenes=", ".join(scenery.LANDSCAPES),
                                  custom_help=custom.prompt_help(), icons=", ".join(emoji.catalog_names()),
                                  parts=", ".join(parts), kinds=kinds, colors=", ".join(explain.COLORS))
        schema = ANIM_SCHEMA
    else:
        rules = IMAGE_RULES.format(style_hint=config.VISUAL_STYLES[style]["hint"])
        schema = IMAGE_SCHEMA
    prompt = PROMPT.format(
        category=category, lang=config.LANGUAGE, history=used,
        scene_rules=rules, scene_schema=schema.replace("{{", "{").replace("}}", "}"),
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
                _validate(data, style)
                _fix_hook(data)
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


def _fix_hook(data: dict):
    h = data.get("hook_title")
    h = h.strip().strip('"') if isinstance(h, str) else ""
    if not h:
        h = data.get("title") if isinstance(data.get("title"), str) else ""
    for k in ("topic", "title", "caption"):  # campos que el resto del bot da por hechos
        if not isinstance(data.get(k), str) or not data[k].strip():
            raise ValueError(f"falta {k}")
    if not isinstance(data.get("hashtags"), list):
        data["hashtags"] = []
    data["hashtags"] = [t for t in data["hashtags"] if isinstance(t, str)]
    words = h.split()
    data["hook_title"] = " ".join(words[:7])


def _validate(data: dict, style: str = "animado"):
    scenes = data.get("scenes") or []
    if len(scenes) < 6:
        raise ValueError("muy pocas escenas")
    if any(not isinstance(s, dict) or not isinstance(s.get("text"), str) for s in scenes):
        raise ValueError("escena sin texto")
    words = sum(len(s["text"].split()) for s in scenes)
    if words < 70 or words > 220:
        raise ValueError(f"longitud rara: {words} palabras")
    for s in scenes:
        if not isinstance(s, dict) or not _str(s.get("text")):
            raise ValueError("escena sin texto")
        if style != "animado" and not s.get("image_prompt"):
            raise ValueError("escena sin image_prompt")
    if style == "animado":
        _clean_anim(scenes)


def _str(v) -> str:
    return v.strip() if isinstance(v, str) else ""


def _clean_anim(scenes: list):
    """Corrige valores que la IA se invente para que la animación nunca falle."""
    from src import anim, catalog, creatures, custom, emoji, explain, scenery  # noqa: F401
    bgs = list(anim.BACKGROUNDS)
    prev = None
    for i, s in enumerate(scenes):
        try:
            a = _str(s.get("action")).lower()
            if a not in anim.ACTIONS or a == prev:
                a = random.choice([x for x in anim.ACTIONS if x != prev and x not in ("walk", "run")])
            s["action"] = prev = a
            raw = s.get("props") if isinstance(s.get("props"), list) else []
            sec = _str(s.get("second")).lower()
            s["second"] = sec if sec in anim.ACTIONS and sec not in ("walk", "run") else ""
            s["keyword"] = _str(s.get("keyword")).upper()[:22]
            s["subject"] = ""  # sin dibujos de IA: solo monigotes, objetos y criaturas animadas

            cr = _str(s.get("creature")).lower().replace(" ", "_")
            icon = emoji.find(_str(s.get("icon")))
            if cr == "custom" or (cr not in creatures.CREATURES and isinstance(s.get("custom"), dict)):
                cr = custom.build(s.get("custom")) or ""
            elif cr and cr not in creatures.CREATURES:
                icon = icon or emoji.find(cr)  # algo que no está dibujado: se busca en los iconos
                cr = ""
            s["creature"] = cr if cr in creatures.CREATURES else ""
            s["icon"] = icon if not s["creature"] else None
            props = []
            for pr in raw[:3]:
                pr = _str(pr).lower()
                if pr in anim.PROPS:
                    props.append(pr)
                elif emoji.find(pr):
                    props.append("emoji:" + emoji.find(pr))
            s["props"] = props
            s["xray"] = s.get("xray") is True and bool(s["creature"])
            s["zoom"] = explain.clean_zoom(s.get("zoom"))
            s["chart"] = None if s["zoom"] else explain.clean_chart(s.get("chart"))
            if i == 0:  # la 1ª escena lleva el gancho en pantalla: sin lupa ni gráfica que lo tapen
                s["zoom"] = s["chart"] = None
            sc_name = _str(s.get("scene")).lower()
            s["scene"] = sc_name if sc_name in scenery.LANDSCAPES else ""
            bg = _str(s.get("bg")).lower()
            if bg not in anim.BACKGROUNDS or (i and bg == scenes[i - 1].get("bg")):
                bg = bgs[i % len(bgs)]
            s["bg"] = bg
        except Exception as e:  # una escena rara nunca tumba el vídeo: se deja en lo básico
            print(f"[guion] escena {i} simplificada por datos raros: {e}")
            simplify_scene(s, bgs[i % len(bgs)])


def simplify_scene(s: dict, bg: str = "azul"):
    """Deja la escena en lo mínimo que siempre se puede dibujar (monigote hablando)."""
    text = s.get("text")
    keep = {"text": text, "action": "talk", "second": "", "keyword": "", "props": [], "creature": "", "icon": None,
            "xray": False, "zoom": None, "chart": None, "scene": "", "bg": bg, "subject": ""}
    s.clear()
    s.update(keep)
