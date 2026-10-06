#!/usr/bin/env python3
"""Publish a daily news story from _pending/news/<date>.json to the live site and social queue.

Usage: python3 scripts/publish-news.py <YYYY-MM-DD> [--social-time "YYYY-MM-DD HH:MM"]

Checks the draft, then:
  1. inserts the story at the top of news.html (below <!-- news:items -->)
  2. replaces the "Today's AI news" block on index.html
  3. adds an <item> to feed.xml
  4. adds the social post to _pending/social-queue.json, renders its graphic and
     approves it for 19:00 UK time on the story's date (or the next day if that has
     passed). --social-time overrides the slot.
Nothing is written unless every check passes. Afterwards: commit and push.

Draft shape (all text plain, no HTML, no em dashes):
{
  "date": "2026-10-06", "slug": "chatgpt-picture-ads", "company": "OpenAI",
  "headline": "...", "summary": "one sentence for the homepage and RSS",
  "body": ["paragraph", "paragraph"], "do_this": ["action", "action"],
  "source_url": "https://...", "source_name": "OpenAI's announcement",
  "checked_sources": ["https://...", ...],
  "social": {"Topic": "...", "Caption Notes": "...", "x_text": "...",
             "graphic": {"headline": "...", "highlight": "...", "lines": [...], "source": "..."},
             "alt_text": "..."}
}
"""
import html
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "_pending" / "news"
NEWS = ROOT / "news.html"
INDEX = ROOT / "index.html"
FEED = ROOT / "feed.xml"
QUEUE = ROOT / "_pending" / "social-queue.json"
SITE = "https://www.ainofluff.co.uk/"
UK = ZoneInfo("Europe/London")
ITEMS_MARKER = "    <!-- news:items -->\n"
LATEST = re.compile(r"(    <!-- news:latest[^\n]*-->\n).*?(    <!-- /news:latest -->)", re.S)
FEED_MARKER = "    <language>en-gb</language>\n"
BANNED = ["—"]
TEXT_FIELDS = ["headline", "summary", "company", "source_name"]
SOCIAL_FIELDS = ["Topic", "Caption Notes", "x_text", "graphic", "alt_text"]

e = html.escape


def fail(problems):
    sys.exit("Not published:\n- " + "\n- ".join(problems))


def check(d, date, news, index, feed, queue):
    p = []
    for k in TEXT_FIELDS + ["slug", "source_url"]:
        if not isinstance(d.get(k), str) or not d[k].strip():
            p.append(f"missing {k}")
    for k in ["body", "checked_sources"]:
        if not isinstance(d.get(k), list) or not d[k]:
            p.append(f"missing {k} (a non-empty list)")
    if d.get("date") != date:
        p.append(f"draft date {d.get('date')!r} doesn't match {date}")
    if p:
        fail(p)
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", d["slug"]):
        p.append("slug must be lowercase words joined by hyphens")
    texts = [d[k] for k in TEXT_FIELDS] + d["body"] + d.get("do_this", [])
    social = d.get("social") or {}
    texts += [json.dumps(social, ensure_ascii=False)]
    for t in texts:
        for b in BANNED:
            if b in t:
                p.append(f"an em dash (STYLE.md) in: {t[:60]}...")
    if not d["source_url"].startswith("https://"):
        p.append("source_url must be https")
    if d["source_url"] not in d["checked_sources"]:
        p.append("source_url must also be listed in checked_sources")
    if f'href="{e(d["source_url"])}"' in news:
        p.append(f"news.html already links {d['source_url']}")
    nid = f"n-{date}-{d['slug']}"
    if f'id="{nid}"' in news:
        p.append(f"news.html already has {nid}")
    if ITEMS_MARKER not in news:
        p.append("news.html is missing the <!-- news:items --> marker")
    if not LATEST.search(index):
        p.append("index.html is missing the news:latest markers")
    if FEED_MARKER not in feed:
        p.append("feed.xml is missing the <language> line")
    if len(d["headline"]) > 110:
        p.append("headline is over 110 characters")
    if social:
        missing = [k for k in SOCIAL_FIELDS if not social.get(k)]
        if missing:
            p.append(f"social is missing {', '.join(missing)}")
        if len(social.get("x_text", "")) > 280:
            p.append("social x_text is over 280 characters")
        last = (social.get("Caption Notes") or "").rstrip().splitlines()[-1:]
        if not last or not last[0].startswith("Source:"):
            p.append("social caption's last line must start with 'Source:'")
        existing = next((q for q in queue if q.get("id") == f"{date}-{d['slug']}"), None)
        if existing and existing.get("Status") not in ("hold", "publer"):
            p.append(f"queue already has {date}-{d['slug']} with status {existing.get('Status')!r}")
    if p:
        fail(p)
    return nid


def article(d, nid, day):
    body = "".join(f'      <p class="news-text">{e(t)}</p>\n' for t in d["body"])
    do = ""
    if d.get("do_this"):
        items = "".join(f"          <li>{e(t)}</li>\n" for t in d["do_this"])
        do = (f'      <div class="news-do">\n        <p class="news-do-title">What you can do</p>\n'
              f"        <ul>\n{items}        </ul>\n      </div>\n")
    return (f'\n    <article class="news-item" id="{nid}">\n'
            f'      <p class="entry-date">{day.day} {day:%B %Y} · {e(d["company"])}</p>\n'
            f'      <h2 class="news-headline"><a href="#{nid}">{e(d["headline"])}</a></h2>\n'
            f"{body}{do}"
            f'      <a href="{e(d["source_url"])}" class="build-link" target="_blank" rel="noopener">{e(d["source_name"])} ↗</a>\n'
            f"    </article>\n")


def latest(d, nid, day):
    return (f'    <div class="today">\n      <div>\n'
            f'        <p class="today-eyebrow">Today\'s AI news · {day.day} {day:%B}</p>\n'
            f'        <h2 class="today-title"><a href="news.html#{nid}">{e(d["headline"])}</a></h2>\n'
            f'        <p class="today-sum">{e(d["summary"])}</p>\n'
            f'      </div>\n      <a href="news.html" class="today-all">All AI news →</a>\n    </div>\n')


def feed_item(d, nid, day):
    pub = datetime(day.year, day.month, day.day, 7, 0, tzinfo=UK).astimezone(ZoneInfo("UTC"))
    link = f"{SITE}news.html#{nid}"
    return (f"\n    <item>\n      <title>{e(d['headline'])}</title>\n      <link>{link}</link>\n"
            f"      <guid>{link}</guid>\n      <pubDate>{pub:%a, %d %b %Y %H:%M:%S} GMT</pubDate>\n"
            f"      <description>{e(d['summary'])}</description>\n    </item>\n")


def social_slot(day, override):
    if override:
        return override
    slot = datetime(day.year, day.month, day.day, 19, 0, tzinfo=UK)
    now = datetime.now(UK)
    while slot <= now + timedelta(minutes=30):
        slot += timedelta(days=1)
    return f"{slot:%Y-%m-%d %H:%M}"


def main():
    args = sys.argv[1:]
    override = None
    if "--social-time" in args:
        i = args.index("--social-time")
        override = " ".join(args[i + 1:i + 3])
        del args[i:i + 3]
    if len(args) != 1:
        sys.exit(__doc__)
    date = args[0]
    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"{date!r} is not YYYY-MM-DD")
    path = DRAFTS / f"{date}.json"
    if not path.exists():
        found = sorted(x.stem for x in DRAFTS.glob("*.json"))
        sys.exit(f"No draft {path.name}. Drafts: {', '.join(found) or 'none'}")
    d = json.loads(path.read_text())
    news, index, feed = NEWS.read_text(), INDEX.read_text(), FEED.read_text()
    queue = json.loads(QUEUE.read_text())
    nid = check(d, date, news, index, feed, queue)

    news = news.replace(ITEMS_MARKER, ITEMS_MARKER + article(d, nid, day), 1)
    news = re.sub(r"Last updated \d{1,2} [A-Z][a-z]+ \d{4}", f"Last updated {day.day} {day:%B %Y}", news, count=1)
    index = LATEST.sub(lambda m: m.group(1) + latest(d, nid, day) + m.group(2), index, count=1)
    feed = feed.replace(FEED_MARKER, FEED_MARKER + feed_item(d, nid, day), 1)
    NEWS.write_text(news)
    INDEX.write_text(index)
    FEED.write_text(feed)
    print(f"Published {nid} to news.html, index.html and feed.xml")

    social = d.get("social")
    if not social:
        print("No social post in the draft.")
        return
    pid = f"{date}-{d['slug']}"
    post = next((q for q in queue if q.get("id") == pid), None)
    if post and post.get("Status") == "publer":
        print(f"Social post {pid} is already approved; left as is.")
        return
    if not post:
        post = {"id": pid, "added": date, "Date": "", "Platform": "All", "Format": "Photo",
                "Content Type": "AI News", **{k: social[k] for k in SOCIAL_FIELDS},
                "label": "news", "source_url": d["source_url"],
                "checked_sources": d["checked_sources"], "Status": "hold", "Posted At": ""}
        queue.append(post)
        QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")
    py = sys.executable
    subprocess.run([py, str(ROOT / "_pending/graphics-kit/render.py"), pid], cwd=ROOT, check=True)
    subprocess.run([py, str(ROOT / "scripts/approve.py"), pid, social_slot(day, override)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
