"""Voz gratis con edge-tts (voces neuronales de Microsoft) + tiempos de cada palabra."""
import asyncio
import os
import time

import edge_tts

import config


async def _synth(text: str, voice: str, out_mp3: str) -> list:
    try:
        com = edge_tts.Communicate(text, voice, rate=config.VOICE_RATE, boundary="WordBoundary")
    except TypeError:  # versiones antiguas de edge-tts
        com = edge_tts.Communicate(text, voice, rate=config.VOICE_RATE)
    words = []
    with open(out_mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append({"word": chunk["text"], "start": start, "end": start + chunk["duration"] / 1e7})
    return words


FALLBACK = {"es": ["es-ES-AlvaroNeural", "es-MX-JorgeNeural", "es-ES-ElviraNeural"],
            "en": ["en-US-AndrewNeural", "en-US-ChristopherNeural", "en-US-AriaNeural"]}


def synthesize(text: str, out_mp3: str) -> list:
    """Devuelve [{word, start, end}] en segundos. Reintenta y, si hace falta, cambia de voz."""
    first = config.VOICES[config.LANGUAGE]
    voices = [first] + [v for v in FALLBACK.get(config.LANGUAGE, []) if v != first]
    last = None
    for n, voice in enumerate([first] + voices):  # la voz elegida se intenta dos veces
        try:
            words = asyncio.run(_synth(text, voice, out_mp3))
            if words and os.path.getsize(out_mp3) > 2000:
                if voice != first:
                    print(f"[voz] se ha usado la voz de reserva {voice}")
                return words
            last = RuntimeError("edge-tts no devolvió audio o tiempos de palabras")
        except Exception as e:
            last = e
        print(f"[voz] intento {n + 1} con {voice} falló: {last}")
        time.sleep(4 * (n + 1))
    raise RuntimeError(f"No se pudo generar la voz: {last}")
