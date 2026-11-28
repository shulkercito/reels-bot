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
{extra}
Reglas:
- TEMA: tiene que encajar de verdad en la categoría "{category}" (no metas una historia de otra temática).
  Mejor si sale algo que TODO EL MUNDO conoce (un futbolista, un videojuego, una marca, un país, un famoso):
  lo conocido hace que la gente se pare al verlo. Nada de temas que haya que explicar antes de entenderlos.
- GANCHO (lo más importante del vídeo: el 70% de la gente decide en 2 segundos si se queda):
  escribe 5 ganchos MUY distintos, puntúa cada uno del 1 al 10 según lo imposible que es NO quedarse a mirar,
  y usa el de más nota. El gancho NO es una introducción: es el dato más chocante de la historia soltado de golpe.
  Un buen gancho tiene: algo CONCRETO (un nombre conocido, un número, un objeto) + una CONTRADICCIÓN o algo que
  parece imposible. Ejemplos buenos: "Este hombre vendió la Torre Eiffel. Dos veces.", "Fueron 80 soldados y
  volvieron 81.", "Un fallo de código creó al Creeper.", "En Francia te puedes casar con un muerto."
  Ejemplos MALOS (prohibidos): "El oro olímpico más loco", "El trabajo más raro de la historia", "Una historia
  increíble", "El tren de cinco estrellas": superlativos vagos que no dicen qué pasó.
  Prohibido empezar con contexto, fechas o "En el año...", "¿Sabías que...?", "Hoy te cuento...", "Imagina...".
  El elegido es la PRIMERA frase de la narración: MÁXIMO 8 palabras, que se diga en menos de 2 segundos.
  "hook_title" es lo que sale escrito en pantalla desde el primer fotograma: la MISMA promesa en 3-6 palabras,
  con el número o el nombre concreto (nada de "increíble", "loco", "raro", "más ... de la historia").
  "hook_word" es UNA palabra de hook_title (el número, el nombre o la palabra más chocante), que se pinta en rojo.
- La SEGUNDA frase (segundos 2-4) sube la apuesta o abre una pregunta ("Y lo peor es que funcionó.",
  "Nadie sabe de dónde salió el 81."), nunca da contexto aburrido.
- Si la categoría es de "¿por qué...?" u "oficios", el gancho es la PREGUNTA intrigante ("¿Por qué los aviones
  tienen ceniceros si no se puede fumar?", "Hubo gente que cobraba por despertarte a palos en la ventana") y la
  respuesta completa se guarda para el FINAL: da pistas por el camino, pero que nadie pueda irse antes de saberla.
- DURACIÓN: narración total entre {wmin} y {wmax} palabras ({secs}), frases muy cortas, sin emojis.
  Ve al grano: si sobra una frase, quítala.
  Cada frase tiene que aportar algo nuevo: nada de relleno ni de repetir lo ya dicho.
- Tono ENTRETENIDO y cercano, como un colega contándote un cotilleo increíble: con giros, humor y sorpresa.
  NO es una clase de ciencias: nada de tecnicismos ni explicaciones de libro si el tema no lo pide.
  Si es una historia, cuéntala como una historia (personaje, qué pasó, giro final). Guarda un segundo dato
  sorprendente para la mitad del vídeo, para que nadie se vaya.
- Solo hechos reales y comprobables; si hay incertidumbre, dilo ("se cree que...").
- EVITA temas de muertes, ejecuciones, suicidios, asesinatos, accidentes con víctimas, torturas o heridas:
  las plataformas les quitan alcance. Elige historias sorprendentes, divertidas o de ingenio.
- FINAL EN BUCLE: la última frase NO es una despedida ni pide comentar ni seguir; es una frase corta que enlaza
  con la primera, de modo que al repetirse el vídeo se lea seguido (ej. última: "Y todo empezó con una carta.",
  primera: "Este hombre vendió la Torre Eiffel..."). El "sígueme" ya sale escrito en pantalla al final.
- Divide la narración en {smin} a {smax} escenas cortas (una frase o media frase cada una). El texto de las escenas, unido, es la narración completa.
{scene_rules}
- NO repitas ninguno de estos temas ya publicados: {history}

Devuelve SOLO JSON válido con esta forma:
{{
  "topic": "tema concreto en pocas palabras",
  "title": "título corto",
  "hooks": [{{"text": "gancho", "score": 1-10}}, "... (5 en total)"],
  "hook_title": "texto en pantalla, 3-6 palabras, con el dato concreto",
  "hook_word": "la palabra de hook_title que se pinta en rojo",
  "scenes": [{scene_schema}],
  "caption": "descripción de 1-2 frases con gancho; termina con una pregunta para que comenten o invitando a seguir la serie",
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
    weights = [getattr(config, "CATEGORY_WEIGHTS", {}).get(c, 1) for c in options]
    return random.choices(options, weights=weights)[0]


def pick_style(history: list) -> str:
    """VISUAL_STYLE=mix alterna estilos; si no, usa el elegido."""
    if config.VISUAL_STYLE in config.VISUAL_STYLES:
        return config.VISUAL_STYLE
    image_styles = [s for s in config.VISUAL_STYLES if s != "animado"]
    last = history[-1].get("style") if history else None
    options = [s for s in image_styles if s != last] or image_styles
    return random.choice(options)


NO_QUOTA = set()  # modelos que han dicho "sin cupo" (429): no se vuelven a intentar en esta ejecución
RESTING = {}      # modelo -> hora hasta la que se salta por estar saturado (503 seguidos)


def _usable(models):
    now = time.time()
    ok = [m for m in models if m not in NO_QUOTA and RESTING.get(m, 0) < now]
    return ok or [m for m in models if m not in NO_QUOTA] or models


def _quota(r, model):
    if r.status_code == 429 and "quota" in r.text.lower():
        NO_QUOTA.add(model)
        raise LookupError(f"modelo {model} sin cupo hoy")


def _draft(history: list, avoid=()) -> dict:
    if not config.LLM_API_KEY:
        raise RuntimeError("Falta LLM_API_KEY")
    category = config.FORCE_CATEGORY or pick_category(history)
    style = pick_style(history)
    used = ", ".join(dict.fromkeys([h["topic"] for h in history[-150:] if h.get("topic")] + list(avoid))) or "ninguno"
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
        extra=f"\nINDICACIONES ESPECIALES (obligatorias): {config.FORCE_NOTES}\n" if config.FORCE_NOTES else "",
        scene_rules=rules, scene_schema=schema.replace("{{", "{").replace("}}", "}"),
        wmin=config.TARGET_WORDS[0], wmax=config.TARGET_WORDS[1],
        smin=config.TARGET_SCENES[0], smax=config.TARGET_SCENES[1],
        secs=f"unos {round(sum(config.TARGET_WORDS) / 2 / 3.2)} segundos",
    )
    # Si un modelo está saturado (503/429) o no existe (404), prueba el siguiente.
    models = [config.LLM_MODEL]
    if config.LLM_PROVIDER == "gemini":
        models += [m for m in FALLBACK_GEMINI if m != config.LLM_MODEL]

    last_err = None
    models = _usable(models)
    for model in models:
        busy = 0
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
                _quota(r, model)
                if r.status_code in (429, 500, 502, 503, 504):
                    busy += 1
                    if busy >= 2:  # saturado de verdad: descansa 10 min y prueba ya el siguiente modelo
                        RESTING[model] = time.time() + 600
                        raise LookupError(f"modelo {model} saturado ({r.status_code}), lo salto 10 min")
                    raise ConnectionError(f"{r.status_code} servidor saturado: {r.text[:150]}")
                r.raise_for_status()
                data = _extract_json(r.json()["choices"][0]["message"]["content"])
                _validate(data, style)
                _fix_hook(data)
                data["category"] = category
                data["style"] = style
                print(f"[guion] generado con {model} (estilo {style}, {sum(len(x['text'].split()) for x in data['scenes'])} palabras)")
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
    hw = _str(data.get("hook_word")).strip("¡!¿?.,\"'")
    data["hook_word"] = hw if hw and hw.lower() in data["hook_title"].lower() else ""


VAGUE = ("increible", "increíble", "loco", "loca", "raro", "rara", "mas raro", "más raro", "de la historia",
         "sorprendente", "misterio del", "el secreto", "no creeras", "no creerás", "sabias que", "sabías que")


def hook_problem(data: dict) -> str:
    """Devuelve por qué el gancho es flojo (o "" si vale). Un gancho flojo = el vídeo muere en 2 segundos."""
    first = _str(data["scenes"][0].get("text")) if data.get("scenes") else ""
    ht = _str(data.get("hook_title")).lower()
    if len(first.split()) > 9:
        return f"la primera frase es larga ({len(first.split())} palabras): '{first}'"
    low = first.lower()
    for bad in ("en el año", "sabías que", "sabias que", "hoy te", "imagina", "hola"):
        if low.startswith(bad):
            return f"la primera frase empieza con '{bad}'"
    if not any(c.isdigit() for c in ht) and any(v in ht for v in VAGUE) and len(ht.split()) <= 5:
        return f"el texto en pantalla es vago: '{data.get('hook_title')}'"
    return ""


def _validate(data: dict, style: str = "animado"):
    scenes = data.get("scenes") or []
    if len(scenes) < max(4, config.TARGET_SCENES[0] - 1):
        raise ValueError("muy pocas escenas")
    if any(not isinstance(s, dict) or not isinstance(s.get("text"), str) for s in scenes):
        raise ValueError("escena sin texto")
    words = sum(len(s["text"].split()) for s in scenes)
    lo, hi = int(config.TARGET_WORDS[0] * config.MIN_WORDS_FACTOR), int(config.TARGET_WORDS[1] * 1.35)
    if words < lo or words > hi:
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


VERIFY_PROMPT = """Eres un verificador de datos muy estricto. Este guion de un vídeo corto debe contar SOLO hechos reales.
Revisa cada persona, lugar, fecha, cifra y suceso. Marca como problema cualquier cosa inventada, nombres que no
existen, cifras exageradas o hechos que mezclan historias distintas. Las frases de humor u opinión no son problema.

Guion (tema: {topic}):
{text}

Si corriges la escena 0 (el gancho), la corrección debe seguir siendo un gancho: máximo 8 palabras, directa
y chocante, con el dato real (nada de frases de contexto tipo "X empezó haciendo Y antes de Z").

Devuelve SOLO JSON:
{{"real": true/false (false SOLO si la persona o el suceso principal no existieron o la historia entera es falsa;
   una fecha, cifra o detalle equivocado NO es false: se arregla en "correcciones"),
  "problemas": ["..."],
  "correcciones": [{{"escena": número empezando en 0, "texto": "frase corregida con el dato real"}}]}}"""


def _chat(prompt: str, temperature=0.2) -> dict:
    models = [config.LLM_MODEL]
    if config.LLM_PROVIDER == "gemini":
        models += [m for m in FALLBACK_GEMINI if m != config.LLM_MODEL]
    last = None
    models = _usable(models)
    for model in models:
        for attempt in range(2):
            try:
                r = requests.post(f"{config.LLM_BASE_URL}/chat/completions",
                                  headers={"Authorization": f"Bearer {config.LLM_API_KEY}"},
                                  json={"model": model, "messages": [{"role": "user", "content": prompt}],
                                        "temperature": temperature, "response_format": {"type": "json_object"}},
                                  timeout=120)
                if r.status_code == 404:
                    break
                if r.status_code == 429 and "quota" in r.text.lower():
                    NO_QUOTA.add(model)
                    break
                r.raise_for_status()
                return _extract_json(r.json()["choices"][0]["message"]["content"])
            except Exception as e:
                last = e
                time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"verificación sin respuesta: {last}")


def verify(data: dict) -> bool:
    """Segunda pasada: otro "experto" revisa los datos. Corrige frases sueltas; si lo esencial es falso, False."""
    text = "\n".join(f"[{i}] {s['text']}" for i, s in enumerate(data["scenes"]))
    try:
        res = _chat(VERIFY_PROMPT.format(topic=data.get("topic", ""), text=text))
    except Exception as e:  # si el verificador no responde, no bloquea la publicación
        print(f"[verificación] no disponible ({e}); sigo sin ella")
        return True
    probs = [p for p in (res.get("problemas") or []) if isinstance(p, str)]
    if res.get("real") is False:
        print(f"[verificación] DESCARTADO: {'; '.join(probs)[:300]}")
        return False
    fixed = 0
    for c in res.get("correcciones") or []:
        try:
            i, t = int(c.get("escena")), _str(c.get("texto"))
            if 0 <= i < len(data["scenes"]) and 2 <= len(t.split()) <= 3 * len(data["scenes"][i]["text"].split()) + 8:
                data["scenes"][i]["text"] = t
                fixed += 1
        except Exception:
            pass
    if hook_problem(data):  # la corrección ha dejado el gancho flojo: mejor otro guion
        print(f"[verificación] el gancho corregido quedó flojo ({hook_problem(data)}); pido otro guion")
        return False
    print(f"[verificación] OK ({fixed} frases corregidas){': ' + '; '.join(probs)[:300] if probs else ''}")
    return True


_STOP = set("el la los las un una unos unas de del al a en y o que por para con su sus se lo es historia real verdadera "
             "misterio misterioso caso increíble increible".split())


def _keys(text: str) -> set:
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", str(text).lower()).encode("ascii", "ignore").decode()
    return {w for w in re.findall(r"[a-z0-9]+", t) if len(w) > 2 and w not in _STOP}


def is_repeat(data: dict, history: list) -> str:
    """Devuelve el tema anterior si este guion repite uno ya publicado (mismo tema o casi las mismas palabras clave)."""
    new = _keys(data.get("topic", ""))
    if not new:
        return ""
    for h in history[-400:]:
        old = _keys(h.get("topic", ""))
        if old and (new == old or len(new & old) / len(new | old) >= 0.6
                    or (len(old) >= 2 and old <= new) or (len(new) >= 2 and new <= old)):
            return h.get("topic", "")
    return ""


def generate(history: list) -> dict:
    """Escribe el guion, comprueba que no repite tema y lo verifica; si falla, prueba con otro (hasta 4)."""
    avoid = []
    for _ in range(4):
        data = _draft(history, avoid)
        rep = is_repeat(data, history)
        if rep:
            print(f"[guion] REPETIDO ('{data.get('topic')}' ya salió como '{rep}'); pido otro tema")
            avoid.append(data.get("topic", ""))
            continue
        weak = hook_problem(data)
        if weak and _ < 3:
            print(f"[guion] GANCHO FLOJO ({weak}); pido otro guion")
            avoid.append(data.get("topic", ""))
            continue
        if verify(data):
            return data
        avoid.append(data.get("topic", ""))
    raise RuntimeError("Ningún guion pasó la verificación de datos (no se publica nada dudoso)")
