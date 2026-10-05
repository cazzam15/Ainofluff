# Tools routine: weekly draft for tools.html

You draft the next update for the **New AI tools** page on ainofluff.co.uk (`tools.html`).
Readers are UK small business owners who aren't technical. Nothing you write is published.
Your draft waits in `_pending/tools/` until Caroline approves it with
`scripts/approve-tools.py`.

## Step 0: setup

- Run `TZ=Europe/London date +%F` and use that as today's date. Don't trust your training
  data about what is current.
- If `tools.html` or `scripts/approve-tools.py` is missing, stop. Write nothing, commit
  nothing, and report that the tools page (PR #6) hasn't been merged yet.
- Read `STYLE.md` in full. Every line you write must follow it.
- Read `tools.html` in full. Note every tool and every source link already on the page.
- List `_pending/tools/`. If a draft other than today's is still waiting there, leave it
  alone and don't repeat its tools.
- Test WebFetch once on https://www.gov.uk. **If WebFetch is blocked (HTTP 403 or no
  network), stop.** Write nothing, commit nothing, and report that the run was skipped
  because sources could not be fetched. Never fall back to search snippets.

## Step 1: find tools

Use WebSearch for launches and changes from the **last 7 days** in tools that UK small
businesses already pay for or use: ChatGPT, Claude, Gemini, Microsoft 365 Copilot, Google
Workspace, Canva, Shopify, Etsy, Squarespace, Wix, Xero, QuickBooks, Sage, FreeAgent,
HubSpot, Mailchimp, Meta (Facebook, Instagram, WhatsApp Business) and similar.

Good entries: a new feature someone could switch on this week, a price change, a free tier,
a UK launch, or a change that forces action (a feature being retired, a deadline).

Skip funding news, model benchmarks, developer-only APIs, research papers and enterprise-only
features. Skip anything already on `tools.html` or in a waiting draft.

Aim for 3 to 5 entries. Fewer is fine. If nothing qualifies, write nothing and say so.

## Step 2: fact-check against the original source

For every entry, fetch the company's own announcement, help page or release notes with
WebFetch. News sites and roundups can point you to a launch, but they never count as the
source.

- Check every date, price, plan name and claim against the fetched original.
- Find out whether it's available in the UK. If the source names countries, use them. If it
  says nothing, write that the company hasn't said which countries get it.
- Prices in GBP only when the source gives GBP. Never convert dollars yourself.
- **If any claim can't be checked against a fetched original, drop the claim or the entry.**
- If a page blocks WebFetch, look for another original page from the same company. If there
  isn't one, drop the entry.

## Step 3: write the draft

Write `_pending/tools/<today>.html` containing exactly one block in this shape, entries
newest first, with real characters (£, curly quotes) and no em dashes:

```html
    <section class="update" aria-labelledby="u-2026-10-12">
      <h2 class="update-head" id="u-2026-10-12">Update: 12 October 2026</h2>
      <ul class="build-list">

        <li class="build">
          <div>
            <p class="entry-date">8 October 2026 · Company</p>
            <h3 class="build-name">Short, plain name of the change</h3>
            <p class="build-desc">What it does for a small business owner, in 2 to 4 sentences.</p>
            <p class="build-desc">UK availability, price or plan, and one practical thing to do.</p>
          </div>
          <div class="build-side">
            <span class="status">Rolling out now</span>
            <a href="https://original-source" class="build-link" target="_blank" rel="noopener">Company's announcement ↗</a>
          </div>
        </li>

      </ul>
    </section>
```

Status labels, pick one per entry:
- `<span class="status">` for anything a UK business can use now or soon: "Available now",
  "Rolling out now", "Free on every plan", or a short price such as "£5 a month".
- `<span class="status no">Not in the UK yet</span>` when the source excludes the UK.
- `<span class="status warn">Action needed</span>` for retirements, deadlines and changes
  that break something.

Each entry has exactly one `build-link`, pointing to the original source. Don't link to a URL
that's already on `tools.html`.

Then write `_pending/tools/<today>.sources.md`: for each entry, its heading, every URL you
fetched, and each factual claim with the URL that confirms it.

Reread the draft against STYLE.md and revise the weakest lines before committing.

## Step 4: check and commit

- Run `python3 - <<'EOF'` with a check that the draft holds one `<section class="update"`,
  has `id="u-<today>"`, contains no `—`, and has one `class="build-link"` per
  `<li class="build">`. Fix anything that fails.
- Stage with `git add _pending/tools/` only.
- Run `git diff --cached --name-only`. **Every path must start with `_pending/tools/`.**
  Unstage anything else. Never edit `tools.html`, `scripts/`, the other HTML pages or
  `feed.xml`.
- Commit on `main` with a message listing the entries, then push. If the push is rejected,
  `git pull --rebase` and push again.

## Report

Finish with:
- if the run was skipped, why, first
- each entry: heading, UK status, source URL
- launches you found but dropped, and the claim that couldn't be checked
- the approve command: `python3 scripts/approve-tools.py <today>`
