# _pending — staging area for the AI news automation

Nothing in this folder is published. The leading underscore means GitHub Pages
(Jekyll) excludes the whole directory from the built site, so these files are not
reachable at ainofluff.co.uk. They ARE visible in the public GitHub repo.

Two cloud routines write here on a schedule. Caroline reviews, then promotes.

## social-queue.json

Social post ideas waiting to go into the content Google Sheet
(`1K9z8FRvL-PPXkZJS-udl-bMsqHvkuliQIHOfyAnLGCo`).

A JSON array. Each object maps 1:1 onto a row of that sheet:

```json
{
  "Date": "2026-07-29",
  "Platform": "All",
  "Format": "Photo",
  "Content Type": "AI News",
  "Topic": "short headline-style topic, this is what the post is about",
  "Caption Notes": "what the post should say, in Caroline's voice, plus the CTA",
  "Visual Notes": "what the graphic or slides should show",
  "Status": "Ready",
  "Posted At": "",
  "_sources": ["https://…", "https://…"]
}
```

`_sources` is extra — it is NOT a sheet column. It exists so the news can be
fact-checked before posting. The sync step drops it.

Entries are appended. The sync step removes what it has copied across, so a
non-empty file means "not yet in the sheet".

## posts/

Draft blog posts as full `.html` files, matching the structure of the live posts
in `/posts/`. A draft here is NOT on the site — promoting it means:

1. `git mv _pending/posts/<name>.html posts/<name>.html`
2. Add its card to the post grid in `index.html`
3. Add its `<item>` to `feed.xml`

Each draft has a sibling `<name>.sources.md` listing every claim and where it
came from. Check those before promoting — AI news moves fast and gets reported
wrong, and a blog post is public and indexed.
