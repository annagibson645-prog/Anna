"""Curate Alex Hormozi's long-form YouTube videos into videos.csv / videos.json."""
import csv, json, sys
import yt_dlp

CHANNEL = "https://www.youtube.com/@AlexHormozi"
MIN_SECONDS = 20 * 60


def list_tab(tab):
    opts = {"quiet": True, "extract_flat": True, "skip_download": True, "ignore_no_formats_error": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"{CHANNEL}/{tab}", download=False)
    return [e for e in info.get("entries", []) if e and e.get("id")]


def enrich(video_id):
    opts = {"quiet": True, "skip_download": True, "ignore_no_formats_error": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except Exception:
        return {}


def fmt_dur(s):
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def main():
    videos = list_tab("videos")
    shorts = list_tab("shorts")
    print(f"videos tab: {len(videos)} | shorts tab: {len(shorts)}", file=sys.stderr)
    rows = []
    for e in videos:
        dur = e.get("duration")
        if dur is None:  # flat listing sometimes omits duration
            dur = enrich(e["id"]).get("duration") or 0
        if dur < MIN_SECONDS:
            continue
        rows.append({
            "title": e.get("title", ""),
            "url": f"https://www.youtube.com/watch?v={e['id']}",
            "duration_min": round(dur / 60),
            "duration": fmt_dur(dur),
            "views": e.get("view_count") or 0,
            "upload_date": e.get("upload_date") or "",
        })
    rows.sort(key=lambda r: r["views"], reverse=True)
    stats = {"videos_tab": len(videos), "shorts_tab": len(shorts), "kept_20min_plus": len(rows)}
    with open("videos.json", "w") as f:
        json.dump({"stats": stats, "videos": rows}, f, indent=1)
    with open("videos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["title"])
        w.writeheader(); w.writerows(rows)
    print(stats, file=sys.stderr)


if __name__ == "__main__":
    main()
