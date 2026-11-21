"""Genera música de fondo ORIGINAL por síntesis (sin copyright: la crea este script).

Uso: python -m tools.make_music   ->  assets/music/*.mp3

Cada pista es un bucle de 16 compases con un aire "curioso/juguetón" (marimba o pizzicato, bajo,
percusión suave) pensado para ir muy bajito debajo de la voz.
"""
import os
import subprocess
import wave

import numpy as np

SR = 44100
OUT = "assets/music"

NOTES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def freq(name: str) -> float:
    n, octv = name[:-1], int(name[-1])
    semis = NOTES[n[0]] + (1 if "#" in n else -1 if "b" in n[1:] else 0)
    return 440.0 * 2 ** ((semis + 12 * (octv + 1) - 69) / 12)


def env(n, attack=0.005, decay=0.25):
    t = np.arange(n) / SR
    e = np.minimum(1, t / attack) * np.exp(-t / decay)
    return e


def marimba(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)
    return vel * s * env(n, 0.002, 0.22)


def pizz(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * k * t) / k ** 1.3 for k in range(1, 7))
    return vel * 0.6 * s * env(n, 0.003, 0.12)


def bell(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 3.5 * t) * np.exp(-t / 0.3))
    return vel * 0.5 * s * env(n, 0.004, 0.6)


def bass(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2 * t)
    return vel * s * env(n, 0.01, 0.35)


def pad(freqs, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs) / len(freqs)
    a = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return vel * s * a


def kick(dur=0.3):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 50 + 80 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12)


def hat(dur=0.08, rng=np.random.default_rng(1)):
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    noise = np.diff(noise, prepend=0)  # filtro paso alto simple
    return 0.25 * noise * env(n, 0.001, 0.02)


def snap(dur=0.15, rng=np.random.default_rng(2)):
    n = int(dur * SR)
    return 0.4 * rng.standard_normal(n) * env(n, 0.001, 0.04)


def place(buf, sig, at):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    if i < len(buf):
        buf[i:j] += sig[: j - i]


# progresiones (acordes como listas de notas) y escalas para la melodía
TRACKS = [
    dict(name="curioso_marimba", bpm=112, inst=marimba, chords=[["C3", "E3", "G3"], ["A2", "C3", "E3"], ["F2", "A2", "C3"], ["G2", "B2", "D3"]],
         scale=["C5", "D5", "E5", "G5", "A5", "C6"], seed=3, drums=True),
    dict(name="misterio_pizzicato", bpm=96, inst=pizz, chords=[["A2", "C3", "E3"], ["F2", "A2", "C3"], ["D2", "F2", "A2"], ["E2", "G#2", "B2"]],
         scale=["A4", "B4", "C5", "E5", "F5", "A5"], seed=5, drums=False),
    dict(name="alegre_campanas", bpm=120, inst=bell, chords=[["F2", "A2", "C3"], ["G2", "B2", "D3"], ["E2", "G2", "B2"], ["A2", "C3", "E3"]],
         scale=["C5", "D5", "F5", "G5", "A5", "C6"], seed=7, drums=True),
    dict(name="travieso_pizz", bpm=128, inst=pizz, chords=[["D3", "F3", "A3"], ["G2", "Bb2", "D3"], ["C3", "E3", "G3"], ["A2", "C#3", "E3"]],
         scale=["D5", "E5", "F5", "A5", "C6", "D6"], seed=11, drums=True),
    dict(name="tranquilo_marimba", bpm=90, inst=marimba, chords=[["C3", "E3", "G3"], ["G2", "B2", "D3"], ["A2", "C3", "E3"], ["F2", "A2", "C3"]],
         scale=["E5", "G5", "A5", "C6", "D6"], seed=13, drums=False),
]


def make(tr):
    rng = np.random.default_rng(tr["seed"])
    beat = 60 / tr["bpm"]
    bars = 16
    total = bars * 4 * beat
    buf = np.zeros(int(total * SR) + SR)
    motif = [(rng.choice(tr["scale"]), rng.choice([0.5, 0.5, 1.0])) for _ in range(8)]
    for bar in range(bars):
        ch = tr["chords"][bar % 4]
        t0 = bar * 4 * beat
        place(buf, pad([freq(n) * 2 for n in ch], 4 * beat, 0.10), t0)
        for b in range(4):  # bajo en negras con salto de quinta
            root = freq(ch[0]) / 2 * (1.5 if b == 2 else 1)
            place(buf, bass(root, beat * 0.9, 0.35), t0 + b * beat)
        for k in range(8):  # arpegio en corcheas
            n = ch[(k * 2 + bar) % 3]
            place(buf, tr["inst"](freq(n) * 2, beat, 0.18), t0 + k * beat / 2)
        # melodía: motivo que se repite con variaciones, deja huecos para la voz
        if bar % 2 == 0 or rng.random() < 0.5:
            t = t0
            for note, d in motif:
                if t >= t0 + 4 * beat:
                    break
                if rng.random() < 0.8:
                    place(buf, tr["inst"](freq(note), beat * d * 1.5, 0.30), t)
                t += beat * d
        if tr["drums"]:
            for b in range(4):
                if b in (0, 2):
                    place(buf, kick(), t0 + b * beat, )
                else:
                    place(buf, snap(), t0 + b * beat)
                place(buf, hat(), t0 + b * beat + beat / 2)
    # cola que se suma al principio para que el bucle sea continuo
    tail = buf[int(total * SR):]
    buf = buf[: int(total * SR)]
    buf[: len(tail)] += tail
    # reverb barata (ecos suaves) y normalización
    for d, g in ((0.11, 0.25), (0.23, 0.15), (0.37, 0.08)):
        buf = buf + g * np.roll(buf, int(d * SR))
    buf = buf / np.max(np.abs(buf)) * 0.8
    st = np.stack([buf, np.roll(buf, int(0.012 * SR))], axis=1)  # pequeño ensanche estéreo
    return (st * 32767).astype(np.int16)


def main():
    os.makedirs(OUT, exist_ok=True)
    for tr in TRACKS:
        pcm = make(tr)
        wav_path = f"{OUT}/{tr['name']}.wav"
        with wave.open(wav_path, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        mp3 = wav_path[:-4] + ".mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "128k", mp3], check=True)
        os.remove(wav_path)
        print(mp3, f"{len(pcm) / SR:.1f} s")


if __name__ == "__main__":
    main()
