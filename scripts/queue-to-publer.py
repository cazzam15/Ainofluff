#!/usr/bin/env python3
"""Export posts with status "publer" from _pending/social-queue.json to Publer bulk-import CSVs.

Writes exports/publer-fb-ig.csv (full caption). X export is paused; x_text stays in the queue.
Each exported post needs: Date (YYYY-MM-DD HH:MM), Caption Notes, media, alt_text.
media and alt_text can be a string or a list (carousel); alt_text needs one entry per image.
Optional: label (defaults to "news"). The Comment(s) column is always left empty: Publer's
free plan doesn't allow first comments. source_url stays in the queue as a record only.
Posts are stamped with exported_at once written, and skipped on later runs.
Posts whose Date has already passed (for example daily news you import a few days late)
move to the next free day at 19:00 UK time, one post per day, and the script lists them.
"""
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "_pending" / "social-queue.json"
OUT = ROOT / "exports"
MEDIA_BASE = "https://www.ainofluff.co.uk/social/"
DEFAULT_LABEL = "news"

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
SLOT_HOUR = 19


def reschedule_past(queue, posts):
    """Move posts dated in the past to the next free day at SLOT_HOUR, in date order."""
    now = datetime.now()
    taken = set()
    for p in queue:
        try:
            taken.add(datetime.strptime(p.get("Date", ""), "%Y-%m-%d %H:%M").date())
        except ValueError:
            pass
    late = []
    for p in posts:
        try:
            when = datetime.strptime(p.get("Date", ""), "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if when <= now + timedelta(minutes=30):
            late.append((when, p))
    slot = now.replace(hour=SLOT_HOUR, minute=0, second=0, microsecond=0)
    for when, p in sorted(late, key=lambda x: x[0]):
        while slot <= now + timedelta(minutes=30) or slot.date() in taken:
            slot += timedelta(days=1)
        p["Date"] = slot.strftime("%Y-%m-%d %H:%M")
        taken.add(slot.date())
        print(f"Rescheduled {p.get('id') or p.get('Topic')!r}: {when:%Y-%m-%d %H:%M} has passed, now {p['Date']}")


def as_list(v):
    return v if isinstance(v, list) else [v]


def row(post, text):
    r = dict.fromkeys(HEADER, "")
    r[HEADER[0]] = post["Date"]
    r[HEADER[1]] = text
    r[HEADER[3]] = ",".join(MEDIA_BASE + m for m in as_list(post["media"]))
    r[HEADER[5]] = post.get("label", DEFAULT_LABEL)
    r[HEADER[6]] = "||".join(as_list(post["alt_text"]))
    return [r[h] for h in HEADER]


def main():
    queue = json.loads(QUEUE.read_text())
    posts = [p for p in queue if p.get("Status") == "publer" and not p.get("exported_at")]
    reschedule_past(queue, posts)
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
        for m in as_list(p["media"]):
            if not (ROOT / "social" / m).is_file():
                errors.append(f"{p['Topic']!r}: social/{m} not found")
        if len(as_list(p["alt_text"])) != len(as_list(p["media"])):
            errors.append(f"{p['Topic']!r}: {len(as_list(p['media']))} images but {len(as_list(p['alt_text']))} alt texts")
    if errors:
        sys.exit("Not exported:\n  " + "\n  ".join(errors))
    if not posts:
        sys.exit('No new posts with status "publer" to export.')

    OUT.mkdir(exist_ok=True)
    out = OUT / "publer-fb-ig.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(HEADER)
        for p in posts:
            w.writerow(row(p, p["Caption Notes"]))
    print(f"Wrote {out} ({len(posts)} posts)")

    today = date.today().isoformat()
    for p in posts:
        p["exported_at"] = today
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")
    print(f"Marked {len(posts)} posts as exported in {QUEUE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
