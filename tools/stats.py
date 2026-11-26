"""Informe de estadísticas de los vídeos publicados (YouTube + Instagram), con las mismas claves del bot.

Uso: python -m tools.stats   -> imprime una tabla y guarda output/stats.json
No publica ni cambia nada: solo lee.
"""
import json
import os

import requests

import config


def yt_stats(ids):
    from src import youtube
    if not youtube.enabled():
        return {}, None, "YouTube sin configurar"
    tok = youtube._access_token()
    h = {"Authorization": f"Bearer {tok}"}
    out, err = {}, None
    for i in range(0, len(ids), 50):
        r = requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, timeout=30,
                         params={"part": "statistics,contentDetails,snippet", "id": ",".join(ids[i:i + 50])})
        if r.status_code != 200:
            err = f"YouTube {r.status_code}: {r.text[:200]}"
            break
        for it in r.json().get("items", []):
            s = it.get("statistics", {})
            out[it["id"]] = {"views": int(s.get("viewCount", 0)), "likes": int(s.get("likeCount", 0)),
                             "comments": int(s.get("commentCount", 0)),
                             "duration": it.get("contentDetails", {}).get("duration"),
                             "published": it.get("snippet", {}).get("publishedAt")}
    chan = None
    r = requests.get("https://www.googleapis.com/youtube/v3/channels", headers=h, timeout=30,
                     params={"part": "statistics", "mine": "true"})
    if r.status_code == 200 and r.json().get("items"):
        chan = r.json()["items"][0]["statistics"]
    return out, chan, err


def ig_stats(ids):
    from src import instagram
    if not (config.IG_USER_ID and config.IG_ACCESS_TOKEN):
        return {}, None, "Instagram sin configurar"
    tok = instagram._token()
    base = instagram._api_base(tok)
    out, err = {}, None
    acc = requests.get(f"{base}/{config.IG_USER_ID}", timeout=30,
                       params={"fields": "followers_count,media_count", "access_token": tok}).json()
    for mid in ids:
        d = {}
        r = requests.get(f"{base}/{mid}", timeout=30,
                         params={"fields": "like_count,comments_count,timestamp", "access_token": tok})
        if r.status_code == 200:
            d.update(r.json())
        r = requests.get(f"{base}/{mid}/insights", timeout=30, params={
            "metric": "views,reach,saved,shares,total_interactions,ig_reels_avg_watch_time,ig_reels_video_view_total_time",
            "access_token": tok})
        if r.status_code == 200:
            for m in r.json().get("data", []):
                d[m["name"]] = (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
        elif not err:
            err = f"Instagram insights {r.status_code}: {r.text[:200]}"
        out[mid] = d
    return out, acc, err


def main():
    with open(config.HISTORY_FILE, encoding="utf-8") as f:
        history = json.load(f)
    hist = [h for h in history if h.get("youtube_id") or h.get("instagram_id")]
    yt, chan, yerr = yt_stats([h["youtube_id"] for h in hist if h.get("youtube_id")])
    ig, acc, ierr = ig_stats([h["instagram_id"] for h in hist if h.get("instagram_id")])
    rows = []
    for h in hist:
        y, i = yt.get(h.get("youtube_id"), {}), ig.get(h.get("instagram_id"), {})
        rows.append({"date": h.get("date"), "format": h.get("format", "short"), "series": h.get("series"),
                     "category": h.get("category"), "title": h.get("title"), "hook": h.get("hook"),
                     "yt": y, "ig": i})
    print("CANAL YT:", json.dumps(chan), "| CUENTA IG:", json.dumps(acc))
    print("AVISOS:", yerr, "|", ierr)
    print("STATS_JSON_START")
    print(json.dumps(rows, ensure_ascii=False))
    print("STATS_JSON_END")
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(f"{config.OUTPUT_DIR}/stats.json", "w", encoding="utf-8") as f:
        json.dump({"channel": chan, "ig_account": acc, "videos": rows}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
