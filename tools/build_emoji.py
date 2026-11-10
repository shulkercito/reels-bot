"""Empaqueta Fluent Emoji (Microsoft, licencia MIT) en assets/emoji/emoji.tar.xz con un índice.

Uso: python tools/build_emoji.py RUTA/fluentui-emoji/assets
"""
import io
import json
import os
import re
import sys
import tarfile


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def main(src):
    index, files = {}, []
    for folder in sorted(os.listdir(src)):
        d = os.path.join(src, folder)
        meta_p = os.path.join(d, "metadata.json")
        if not os.path.exists(meta_p):
            continue
        svg = None
        for sub in ("Flat", os.path.join("Default", "Flat")):
            p = os.path.join(d, sub)
            if os.path.isdir(p):
                svgs = [f for f in os.listdir(p) if f.endswith(".svg")]
                if svgs:
                    svg = os.path.join(p, svgs[0])
                    break
        if not svg:
            continue
        meta = json.load(open(meta_p, encoding="utf-8"))
        s = slug(folder)
        index[s] = {"name": folder.lower(), "group": meta.get("group", ""),
                    "keywords": sorted({k.lower() for k in meta.get("keywords", [])})}
        files.append((s, svg))
    out = os.path.join(os.path.dirname(__file__), "..", "assets", "emoji", "emoji.tar.xz")
    with tarfile.open(out, "w:xz", preset=9) as tar:
        data = json.dumps(index, ensure_ascii=False).encode()
        ti = tarfile.TarInfo("index.json")
        ti.size = len(data)
        tar.addfile(ti, io.BytesIO(data))
        for s, p in files:
            tar.add(p, arcname=f"svg/{s}.svg")
    print(len(index), "iconos ->", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
