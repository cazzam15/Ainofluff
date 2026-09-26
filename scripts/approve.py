#!/usr/bin/env python3
"""Approve a held post from the news routine so queue-to-publer.py will export it.

Usage: python3 scripts/approve.py <post-id> <YYYY-MM-DD HH:MM>

Moves _pending/graphics/<post-id>.png to social/<post-id>.png, then sets the
post's Status to "publer", its Date to the time given and its media to the
moved graphic. Afterwards: commit, push, wait for the image to load on the
live site, then run scripts/queue-to-publer.py.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE = ROOT / "_pending" / "social-queue.json"
GRAPHICS = ROOT / "_pending" / "graphics"
SOCIAL = ROOT / "social"
EXPORT_FIELDS = ["Caption Notes", "alt_text"]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    post_id = sys.argv[1]
    when = " ".join(sys.argv[2:])
    try:
        scheduled = datetime.strptime(when, "%Y-%m-%d %H:%M")
    except ValueError:
        sys.exit(f"Date {when!r} is not YYYY-MM-DD HH:MM")
    if scheduled <= datetime.now():
        sys.exit(f"{when} is in the past")

    queue = json.loads(QUEUE.read_text())
    post = next((p for p in queue if p.get("id") == post_id), None)
    if not post:
        held = [p["id"] for p in queue if p.get("Status") == "hold" and p.get("id")]
        sys.exit(f"No post with id {post_id!r}. Held posts: {', '.join(held) or 'none'}")
    if post.get("Status") != "hold":
        sys.exit(f"{post_id} has status {post.get('Status')!r}, not 'hold'")
    missing = [k for k in EXPORT_FIELDS if not post.get(k)]
    if missing:
        sys.exit(f"{post_id} is missing {', '.join(missing)}, so it can't be exported")

    src = GRAPHICS / f"{post_id}.png"
    dst = SOCIAL / f"{post_id}.png"
    if not src.is_file():
        sys.exit(f"{src.relative_to(ROOT)} not found. Render it with: "
                 f"python3 _pending/graphics-kit/render.py {post_id}")
    if dst.exists():
        sys.exit(f"{dst.relative_to(ROOT)} already exists")

    SOCIAL.mkdir(exist_ok=True)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(src)],
                             cwd=ROOT, capture_output=True).returncode == 0
    if tracked:
        subprocess.run(["git", "mv", str(src), str(dst)], cwd=ROOT, check=True)
    else:
        shutil.move(src, dst)

    post["Status"] = "publer"
    post["Date"] = when
    post["media"] = dst.name
    QUEUE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n")

    print(f"Approved {post_id} for {when}: graphic moved to {dst.relative_to(ROOT)}")
    print("Next: git add -A _pending social && git commit && git push, "
          "wait for the image to load on the live site, then run scripts/queue-to-publer.py")


if __name__ == "__main__":
    main()
