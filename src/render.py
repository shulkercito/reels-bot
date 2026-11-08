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


def _scene_clip(img: str, dur: float, out: str, i: int, flat: bool = False):
    """Cada escena: 'golpe' de zoom al entrar, movimiento continuo y, a veces, sacudida."""
    W, H, fps = config.WIDTH, config.HEIGHT, config.FPS
    frames = max(int(round(dur * fps)), 1)
    step = 0.14 / frames
    punch = "0.14*exp(-on/4)"                     # entra grande y se asienta en ~0.3 s
    bounce = "0.015*sin(on/3)"                    # respiración/rebote suave
    shake = "if(lt(on,8),18*sin(on*2.7),0)" if i % 3 == 1 else "0"  # sacudida en 1 de cada 3
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    move = i % 4
    if move == 0:    # zoom in
        z, x, y = f"1.04+{punch}+{step}*on+{bounce}", cx, cy
    elif move == 1:  # zoom out
        z, x, y = f"1.18+{punch}-{step}*on+{bounce}", cx, cy
    elif move == 2:  # paneo izquierda -> derecha
        z, x, y = f"1.16+{punch}+{bounce}", f"(iw-iw/zoom)*on/{frames}", cy
    else:            # paneo abajo -> arriba
        z, x, y = f"1.16+{punch}+{bounce}", cx, f"(ih-ih/zoom)*(1-on/{frames})"
    x, y = f"{x}+{shake}", f"{y}+({shake})*0.6"
    look = "eq=contrast=1.04:saturation=1.08" if flat else "eq=contrast=1.06:saturation=1.15,vignette=PI/6"
    vf = (
        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={fps},"
        f"{look},fade=t=in:st=0:d=0.12:color=white,format=yuv420p"
    )
    _run([
        "ffmpeg", "-y", "-i", img, "-vf", vf, "-frames:v", str(frames),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out,
    ])


def render(images: list, durations: list, voice: str, ass: str, out_mp4: str, work: str, style: str = "pixar"):
    clips = []
    for i, (img, dur) in enumerate(zip(images, durations)):
        clip = f"{work}/clip_{i:02d}.mp4"
        _scene_clip(img, dur, clip, i, flat=(style == "monigotes"))
        clips.append(clip)
    concat_list = f"{work}/clips.txt"
    with open(concat_list, "w") as f:
        f.writelines(f"file '{os.path.abspath(c)}'\n" for c in clips)
    finish(["-f", "concat", "-safe", "0", "-i", concat_list], voice, ass, out_mp4)


def render_animated(scenes: list, durations: list, voice: str, ass: str, out_mp4: str, work: str):
    """Animación por código (monigotes que se mueven), sin imágenes de IA."""
    from src import anim
    silent = f"{work}/anim.mp4"
    anim.render_silent(scenes, durations, silent)
    finish(["-i", silent], voice, ass, out_mp4)


def finish(video_input: list, voice: str, ass: str, out_mp4: str):
    """Añade voz, música y subtítulos al vídeo."""
    music = sorted(glob.glob(f"{config.MUSIC_DIR}/*.mp3"))
    total = audio_duration(voice)
    ass_esc = os.path.abspath(ass).replace("\\", "/").replace(":", "\\:")

    cmd = ["ffmpeg", "-y", *video_input, "-i", voice]
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
        # ajustes recomendados por Instagram para Reels: H.264 High, 30 fps, GOP 2 s, bitrate acotado, AAC estéreo 48 kHz
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-profile:v", "high", "-level", "4.1",
        "-maxrate", "8M", "-bufsize", "16M", "-g", str(config.FPS * 2), "-keyint_min", str(config.FPS),
        "-pix_fmt", "yuv420p", "-r", str(config.FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart", out_mp4,
    ]
    _run(cmd)
