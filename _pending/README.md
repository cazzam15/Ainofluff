# _pending: staging area for the AI news automation

Nothing in this folder is published. The leading underscore means GitHub Pages
(Jekyll) excludes the whole directory from the built site, so these files are not
reachable at ainofluff.co.uk. They ARE visible in the public GitHub repo.

## The flow: hold → approve → Publer

1. **Hold.** The news routine (cloud, Mondays 07:00 UTC) researches AI news,
   fact-checks each story against its original source, and appends up to 3 posts
   to `social-queue.json` with `"Status": "hold"`. For each one it renders a
   graphic to `_pending/graphics/<id>.png` and commits to `main`. It never
   writes outside `_pending/`.
2. **Review.** Pull, then read each held post: caption, `x_text`, graphic and
   `checked_sources`. Edit anything you want to change in place. To redo a
   graphic after editing its `graphic` brief:

   ```
   python3 _pending/graphics-kit/render.py <id>
   ```

   To reject a post, delete it from the queue and delete its PNG.
3. **Approve.** Pick a posting time and run:

   ```
   python3 scripts/approve.py <id> "YYYY-MM-DD HH:MM"
   ```

   This moves the graphic into `social/`, sets `Status` to `"publer"`, fills in
   `Date` and `media`. It refuses posts that aren't on hold, times in the past,
   and posts missing a caption, alt text or graphic.
4. **Push.** Run through `DEPLOY.md`, then commit and push. Wait until
   `https://www.ainofluff.co.uk/social/<id>.png` loads, because Publer fetches
   the image from the live site.
5. **Export.** Run `python3 scripts/queue-to-publer.py`. It writes
   `exports/publer-fb-ig.csv` for every approved post not yet exported and
   stamps each with `exported_at`. Bulk-import the CSV into Publer, then commit
   the queue so the stamps stick.

Held posts you leave alone are pruned by the routine 14 days after their
`added` date, along with their graphic. It never touches approved or exported
posts.

## social-queue.json

A JSON array, UTF-8, 2-space indent. A post as the routine writes it:

```json
{
  "id": "2026-10-05-bank-voice-scam",
  "added": "2026-10-05",
  "Date": "",
  "Platform": "All",
  "Format": "Photo",
  "Content Type": "AI News",
  "Topic": "short headline-style line, unique in the queue",
  "Caption Notes": "the full caption; last line is 'Source: <publisher>, <d Mon yyyy>.'",
  "x_text": "280 characters or fewer (X export is paused, kept for later)",
  "graphic": {"headline": "...", "highlight": "...", "lines": ["...", "..."], "source": "Source: ..."},
  "alt_text": "one sentence describing the graphic",
  "label": "news",
  "source_url": "original source; posted as the first comment",
  "checked_sources": ["every URL fetched to check the story"],
  "Status": "hold",
  "Posted At": ""
}
```

`Status` is `"hold"` until approved, then `"publer"`. `approve.py` adds `media`;
`queue-to-publer.py` adds `exported_at`. Older posts use `_sources` instead of
`checked_sources` and have no `id`; the export script doesn't need either.

Carousels and hand-made posts skip the routine and `approve.py`: put the images
in `social/`, set `media` and `alt_text` as matching lists, set `Status` to
`"publer"` and a `Date`, then export as above.

The old Google Sheet sync (Status `"Ready"`, n8n, Telegram approval) is retired.

## graphics-kit/ and graphics/

`graphics-kit/` holds `render.py`, the HTML template and the two fonts. It turns
a post's `graphic` brief into a 1080x1350 PNG in the house style. It needs
Chromium or Chrome on `PATH`, or the `playwright` Python package.

`graphics/` holds rendered PNGs for posts on hold. Only `approve.py` moves them
into `social/`, which is public.

## posts/

Draft blog posts as full `.html` files, matching the structure of the live posts
in `/posts/`. The blog-draft routine that writes them is paused. A draft here is
NOT on the site. Promoting it means:

1. `git mv _pending/posts/<name>.html posts/<name>.html`
2. Add its card to the post grid in `index.html`
3. Add its `<item>` to `feed.xml`

Each draft has a sibling `<name>.sources.md` listing every claim and where it
came from. Check those before promoting. AI news moves fast and gets reported
wrong, and a blog post is public and indexed.
