"""
Scrape YouTube comments using youtube-comment-downloader (pip package).
Saves comments to a CSV with columns: comment_id, author, text, published_time, likes, source_url, source, scraped_at

Usage:
    python scrape_youtube_comments.py --url "https://www.youtube.com/watch?v=k9a5LpSfp7c" --out comments.csv --max 200

Note: This script tries to use the Python API from `youtube_comment_downloader`. If not available, it will print helpful instructions.
"""
import argparse
import csv
import datetime
import json
import re
import sys

VIDEO_ID_RE = re.compile(r"(?:v=|/videos/|embed/|youtu\.be/)([A-Za-z0-9_-]{11})")


def extract_video_id(url_or_id):
    m = VIDEO_ID_RE.search(url_or_id)
    if m:
        return m.group(1)
    if len(url_or_id) == 11:
        return url_or_id
    raise ValueError("Could not extract video id from input: {}".format(url_or_id))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="YouTube video URL or ID")
    parser.add_argument("--out", required=True, help="Output CSV path")
    parser.add_argument("--max", type=int, default=1000, help="Max comments to fetch")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.url)
    except ValueError as e:
        print("ERROR:", e)
        sys.exit(1)

    downloader = None
    try:
        # try the typical import name
        from youtube_comment_downloader import YoutubeCommentDownloader
        downloader = YoutubeCommentDownloader()
    except Exception:
        downloader = None

    if downloader is None:
        print("Could not import Python API for `youtube-comment-downloader`.")
        print("Ensure it's installed (`pip install youtube-comment-downloader`) and try again.")
        print("If you prefer, use the package's CLI, e.g. `youtube-comment-downloader --url <URL> -o output.json` and convert to CSV.")
        sys.exit(1)

    # try several method names (some forks use different names)
    get_comments_fn = None
    for name in ("get_comments", "get_comments_from_video_id", "get_comments_from_url", "get_comments_from_url_or_id"):
        if hasattr(downloader, name):
            get_comments_fn = getattr(downloader, name)
            break

    if get_comments_fn is None:
        # some implementations return generator from instance itself
        if callable(downloader):
            get_comments_fn = downloader

    if get_comments_fn is None:
        print("Could not find a comment-fetching function on the downloader object. Please check the installed package API.")
        sys.exit(1)

    out_rows = []
    count = 0
    try:
        for item in get_comments_fn(video_id):
            # item may be dict-like or JSON string
            if isinstance(item, str):
                try:
                    item = json.loads(item)
                except Exception:
                    # skip unparsable
                    continue
            # attempt to extract common fields
            text = item.get("text") or item.get("textDisplay") or item.get("comment") or item.get("message") or ""
            author = item.get("author") or item.get("authorDisplayName") or item.get("name") or ""
            comment_id = item.get("cid") or item.get("comment_id") or item.get("id") or ""
            time_published = item.get("time") or item.get("published_time") or ""
            likes = item.get("likes") or item.get("likeCount") or 0

            out_rows.append({
                "comment_id": comment_id,
                "author": author,
                "text": text,
                "published_time": time_published,
                "likes": likes,
                "source_url": args.url,
                "source": "YouTube",
                "scraped_at": datetime.datetime.utcnow().isoformat(),
            })
            count += 1
            if args.max and count >= args.max:
                break
    except KeyboardInterrupt:
        print("Interrupted by user, writing fetched comments...")

    # write CSV
    fieldnames = ["comment_id", "author", "text", "published_time", "likes", "source_url", "source", "scraped_at"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    print(f"Wrote {len(out_rows)} comments to {args.out}")


if __name__ == "__main__":
    main()
