"""Subtítulos estilo viral: 2-3 palabras grandes, la que suena resaltada."""
import re

import config


def _ts(t: float) -> str:
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _clean(w: str) -> str:
    return w.replace("{", "").replace("}", "").replace("\\", "").upper()


def chunk_words(words: list, max_words=3, max_chars=16) -> list:
    """Agrupa palabras en bloques cortos; corta en signos de puntuación."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        text = " ".join(x["word"] for x in cur)
        if len(cur) >= max_words or len(text) >= max_chars or re.search(r"[.,!?;:…]$", w["word"]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def build_ass(words: list, path: str):
    c = config
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {c.WIDTH}
PlayResY: {c.HEIGHT}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,{c.FONT_NAME},{c.FONT_SIZE},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,5,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    y = int(c.HEIGHT * 0.62)
    chunks = chunk_words(words)
    for ci, chunk in enumerate(chunks):
        chunk_end = chunks[ci + 1][0]["start"] if ci + 1 < len(chunks) else chunk[-1]["end"] + 0.4
        for wi, w in enumerate(chunk):
            start = w["start"]
            end = chunk[wi + 1]["start"] if wi + 1 < len(chunk) else chunk_end
            parts = []
            for k, x in enumerate(chunk):
                word = _clean(x["word"])
                parts.append(f"{{\\c{c.HIGHLIGHT_COLOR}}}{word}{{\\c&H00FFFFFF&}}" if k == wi else word)
            # pequeño "pop" al aparecer cada bloque
            anim = "\\fscx85\\fscy85\\t(0,90,\\fscx100\\fscy100)" if wi == 0 else ""
            text = f"{{\\pos({c.WIDTH // 2},{y}){anim}}}" + " ".join(parts)
            lines.append(f"Dialogue: 0,{_ts(start)},{_ts(end)},Main,,0,0,0,,{text}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")
