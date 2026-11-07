"""Montaje con ffmpeg: zoom lento sobre cada imagen + voz + música + subtítulos."""
import glob
import os
import random
import subprocess

import config


def _run(cmd: list):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg falló:\n{p.stderr[-2000:]}")


def audio_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def scene_timings(scenes: list, words: list, total: float) -> list:
    """Reparte la duración entre escenas según dónde empieza su texto en la voz."""
    counts = [len(s["text"].split()) for s in scenes]
    n_text, n_tts = sum(counts), len(words)
    starts, acc = [], 0
    for c in counts:
        idx = min(round(acc / n_text * n_tts), n_tts - 1)
        starts.append(0.0 if not starts else words[idx]["start"])
        acc += c
    ends = starts[1:] + [total]
    return [max(e - s, 0.8) for s, e in zip(starts, ends)]


def _scene_clip(img: str, dur: float, out: str, i: int):
    W, H, fps = config.WIDTH, config.HEIGHT, config.FPS
    frames = max(int(round(dur * fps)), 1)
    step = 0.18 / frames  # ~18 % de zoom a lo largo de la escena
    style = i % 4
    if style == 0:    # zoom in centrado
        z, x, y = f"1+{step}*on", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif style == 1:  # zoom out
        z, x, y = f"1.18-{step}*on", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif style == 2:  # zoom in hacia arriba
        z, x, y = f"1+{step}*on", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*0.25"
    else:             # paneo lateral
        z, x, y = "1.15", f"(iw-iw/zoom)*on/{frames}", "ih/2-(ih/zoom/2)"
    vf = (
        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={fps},"
        "eq=contrast=1.05:saturation=1.1,vignette=PI/5,format=yuv420p"
    )
    _run([
        "ffmpeg", "-y", "-i", img, "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out,
    ])


def render(images: list, durations: list, voice: str, ass: str, out_mp4: str, work: str):
    clips = []
    for i, (img, dur) in enumerate(zip(images, durations)):
        clip = f"{work}/clip_{i:02d}.mp4"
        _scene_clip(img, dur, clip, i)
        clips.append(clip)
    concat_list = f"{work}/clips.txt"
    with open(concat_list, "w") as f:
        f.writelines(f"file '{os.path.abspath(c)}'\n" for c in clips)

    music = sorted(glob.glob(f"{config.MUSIC_DIR}/*.mp3"))
    total = audio_duration(voice)
    ass_esc = os.path.abspath(ass).replace("\\", "/").replace(":", "\\:")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-i", voice]
    if music:
        cmd += ["-stream_loop", "-1", "-i", random.choice(music)]
        afilter = (
            f"[1:a]volume=1.0[v];[2:a]volume={config.MUSIC_VOLUME},afade=t=out:st={max(total - 1.5, 0)}:d=1.5[m];"
            "[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]"
        )
    else:
        afilter = "[1:a]loudnorm=I=-14:TP=-1.5[a]"
    cmd += [
        "-filter_complex", f"[0:v]subtitles='{ass_esc}'[vout];{afilter}",
        "-map", "[vout]", "-map", "[a]",
        "-t", f"{total + 0.3:.2f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-r", str(config.FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", out_mp4,
    ]
    _run(cmd)
