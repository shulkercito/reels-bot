"""Voz gratis con edge-tts (voces neuronales de Microsoft) + tiempos de cada palabra."""
import asyncio

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


def synthesize(text: str, out_mp3: str) -> list:
    """Devuelve [{word, start, end}] en segundos."""
    voice = config.VOICES[config.LANGUAGE]
    words = asyncio.run(_synth(text, voice, out_mp3))
    if not words:
        raise RuntimeError("edge-tts no devolvió tiempos de palabras")
    return words
