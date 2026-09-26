#!/usr/bin/env python3
"""Export posts with status "publer" from _pending/social-queue.json to Publer bulk-import CSVs.

Writes exports/publer-fb-ig.csv (full caption). X export is paused; x_text stays in the queue.
Each exported post needs: Date (YYYY-MM-DD HH:MM), Caption Notes, media, alt_text.
Optional: source_url, posted as a comment.
"""
import csv
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "_pending" / "social-queue.json"
OUT = ROOT / "exports"
MEDIA_BASE = "https://www.ainofluff.co.uk/social/"
LABEL = "news"

HEADER = [
    "Date - Intl. format or prompt",
    "Text",
    "Link(s) - Separated by comma for FB carousels",
    "Media URL(s) - Separated by comma",
    "Title - For the video, pin, PDF ..",
    "Label(s) - Separated by comma",
    "Alt text(s) - Separated by ||",
    "Comment(s) - Separated by ||",
    "Pin board, FB album, or Google category",
    "Post subtype - I.e. story, reel, PDF ..",
    "CTA - For Facebook links or Google",
    "Reminder - For stories, reels, shorts, and TikToks",
]
REQUIRED = ["Date", "Caption Notes", "media", "alt_text"]


def row(post, text, comment):
    r = dict.fromkeys(HEADER, "")
    r[HEADER[0]] = post["Date"]
    r[HEADER[1]] = text
    r[HEADER[3]] = MEDIA_BASE + post["media"]
    r[HEADER[5]] = LABEL
    r[HEADER[6]] = post["alt_text"]
    r[HEADER[7]] = comment
    return [r[h] for h in HEADER]


def main():
    posts = [p for p in json.loads(QUEUE.read_text()) if p.get("Status") == "publer"]
    errors = []
    for p in posts:
        missing = [k for k in REQUIRED if not p.get(k)]
        if missing:
            errors.append(f"{p.get('Topic')!r}: missing {', '.join(missing)}")
            continue
        try:
            datetime.strptime(p["Date"], "%Y-%m-%d %H:%M")
        except ValueError:
            errors.append(f"{p['Topic']!r}: Date {p['Date']!r} is not YYYY-MM-DD HH:MM")
        if not (ROOT / "social" / p["media"]).is_file():
            errors.append(f"{p['Topic']!r}: social/{p['media']} not found")
    if errors:
        sys.exit("Not exported:\n  " + "\n  ".join(errors))
    if not posts:
        sys.exit('No posts with status "publer".')

    OUT.mkdir(exist_ok=True)
    out = OUT / "publer-fb-ig.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(HEADER)
        for p in posts:
            w.writerow(row(p, p["Caption Notes"], p.get("source_url", "")))
    print(f"Wrote {out} ({len(posts)} posts)")


if __name__ == "__main__":
    main()
