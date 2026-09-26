#!/usr/bin/env python3
"""Render a queued post's graphic brief to _pending/graphics/<id>.png (1080x1350).

Usage: python3 _pending/graphics-kit/render.py <post-id>

Reads the post's "graphic" field from _pending/social-queue.json:
  {"headline": "...", "highlight": "part of headline shown in teal (optional)",
   "lines": ["2 or 3 short lines"], "source": "Source: ..."}
Needs Chromium or Chrome on PATH, or the playwright Python package.
"""
import html
import json
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parent
PENDING = KIT.parent
QUEUE = PENDING / "social-queue.json"
OUT_DIR = PENDING / "graphics"
W, H = 1080, 1350


def build_html(g):
    headline = html.escape(g["headline"])
    hl = g.get("highlight")
    if hl:
        if hl not in g["headline"]:
            sys.exit(f"highlight {hl!r} is not part of the headline")
        headline = headline.replace(html.escape(hl), f"<span>{html.escape(hl)}</span>", 1)
    lines = "".join(f"<p>{html.escape(l)}</p>" for l in g["lines"])
    return (KIT / "template.html").read_text().replace("{{HEADLINE}}", headline) \
        .replace("{{LINES}}", lines).replace("{{SOURCE}}", html.escape(g["source"]))


def screenshot(page, out):
    for name in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
        exe = shutil.which(name)
        if exe:
            subprocess.run([exe, "--headless=new", "--no-sandbox", "--hide-scrollbars",
                            "--force-device-scale-factor=1", f"--window-size={W},{H}",
                            "--virtual-time-budget=3000", f"--screenshot={out}", page.as_uri()],
                           check=True, capture_output=True)
            return
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("No Chromium found. Install one: pip install playwright && python3 -m playwright install --with-deps chromium")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(page.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.screenshot(path=str(out))
        b.close()


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    post_id = sys.argv[1]
    post = next((p for p in json.loads(QUEUE.read_text()) if p.get("id") == post_id), None)
    if not post:
        sys.exit(f"No post with id {post_id!r} in {QUEUE}")
    g = post.get("graphic") or {}
    if not g.get("headline") or not 2 <= len(g.get("lines", [])) <= 3 or not g.get("source"):
        sys.exit("graphic needs a headline, 2-3 lines and a source")

    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{post_id}.png"
    # The page must sit next to template.html so the relative font paths resolve.
    with tempfile.NamedTemporaryFile("w", suffix=".html", dir=KIT, delete=False) as f:
        f.write(build_html(g))
        page = Path(f.name)
    try:
        screenshot(page, out)
    finally:
        page.unlink()
    size = struct.unpack(">II", out.read_bytes()[16:24])
    if size != (W, H):
        sys.exit(f"{out} is {size[0]}x{size[1]}, expected {W}x{H}")
    print(f"Wrote {out.relative_to(PENDING.parent)}")


if __name__ == "__main__":
    main()
