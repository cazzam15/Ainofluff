#!/usr/bin/env python3
"""Publish a drafted update from the tools routine onto tools.html.

Usage: python3 scripts/approve-tools.py <YYYY-MM-DD>

Reads _pending/tools/<date>.html (one <section class="update"> block), checks it,
inserts it below the <!-- tools:updates --> marker in tools.html, sets the
"Last updated" line to that date, and deletes the draft and its .sources.md.
Edit the draft first if you want to change or drop an entry. Afterwards: run
through DEPLOY.md, commit and push.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "tools.html"
DRAFTS = ROOT / "_pending" / "tools"
MARKER = "    <!-- tools:updates -->\n"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    date = sys.argv[1]
    try:
        day = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        sys.exit(f"{date!r} is not YYYY-MM-DD")

    draft = DRAFTS / f"{date}.html"
    if not draft.exists():
        found = sorted(p.stem for p in DRAFTS.glob("*.html"))
        sys.exit(f"No draft {draft.name}. Drafts waiting: {', '.join(found) or 'none'}")
    section = draft.read_text().strip("\n") + "\n"
    page = PAGE.read_text()

    problems = []
    if section.count('<section class="update"') != 1 or not section.rstrip().endswith("</section>"):
        problems.append("draft must be exactly one <section class=\"update\"> block")
    if f'id="u-{date}"' not in section:
        problems.append(f'section heading needs id="u-{date}"')
    if "—" in section:
        problems.append("draft contains an em dash (STYLE.md)")
    if f'id="u-{date}"' in page:
        problems.append(f"tools.html already has the {date} update")
    if MARKER not in page:
        problems.append("tools.html is missing the <!-- tools:updates --> marker")
    entries = section.count('<li class="build">')
    links = re.findall(r'<a href="([^"]+)" class="build-link"', section)
    if entries == 0 or len(links) != entries:
        problems.append("every entry needs exactly one source link (class=\"build-link\")")
    for url in links:
        if not url.startswith("https://"):
            problems.append(f"source link is not https: {url}")
        elif f'href="{url}"' in page:
            problems.append(f"source already on the page: {url}")
    if problems:
        sys.exit("Not published:\n- " + "\n- ".join(problems))

    page = page.replace(MARKER, MARKER + "\n" + section + "\n", 1)
    updated = f"Last updated {day.day} {day:%B %Y}"
    page, n = re.subn(r"Last updated \d{1,2} [A-Z][a-z]+ \d{4}", updated, page, count=1)
    if n != 1:
        sys.exit('Could not find the "Last updated" line in tools.html')
    PAGE.write_text(page)

    draft.unlink()
    (DRAFTS / f"{date}.sources.md").unlink(missing_ok=True)
    print(f"Added the {date} update ({entries} entries) to tools.html. "
          "Check it in a browser, then commit and push.")


if __name__ == "__main__":
    main()
