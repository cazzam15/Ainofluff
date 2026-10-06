# Daily news routine: one story, published

You publish one AI news story a day to ainofluff.co.uk (`news.html`, the homepage and
`feed.xml`) and queue a matching social post. **Nobody reviews your work before it goes
live.** Caroline relies on your fact-check, so skipping a day is always better than
publishing something you couldn't check.

Readers are people in the UK who keep hearing about AI and haven't started, plus small
business owners. They aren't technical.

## Step 0: setup

- Run `TZ=Europe/London date +%F` and use that as today's date. Don't trust your training
  data about what is current.
- `git pull`. If `scripts/publish-news.py` or `news.html` is missing, stop and report it.
- If `_pending/news/<today>.json` exists, or `news.html` already has an id starting with
  `n-<today>-`, stop: today is done.
- Read `STYLE.md` in full. Every line you write must follow it.
- Read `news.html`. Note every story and source link already there; don't repeat a story.
  Also skim the post titles on `index.html` and the last 10 `Topic` lines in
  `_pending/social-queue.json` so you don't repeat those either.
- Test WebFetch once on https://www.gov.uk. **If WebFetch is blocked (HTTP 403 or no
  network), stop.** Publish nothing and report that the run was skipped. Never fall back
  to search snippets.

## Step 1: find one story

Use WebSearch for AI news from the **last 48 hours**. Pick the single story that matters
most to an ordinary UK reader. Good picks, best first:

1. Something that changes what people can do or should do this week: a change to
   ChatGPT, Gemini, Claude, Copilot, Meta AI, Apple or Google features people already
   use, a price or plan change, a UK launch, privacy or settings changes.
2. Scams and safety: warnings from UK bodies (Action Fraud, National Trading Standards,
   NCSC, FCA, Ofcom, ICO, banks), with practical steps.
3. UK rules and public services: government, NHS, schools, regulators.
4. Big stories everyone is talking about, explained plainly.

Skip funding rounds, valuations, benchmarks, research papers, developer-only tools and
enterprise-only features. If a story only applies outside the UK, it still works when you
say so plainly and explain what UK readers have now.

## Step 2: fact-check against the original source

Fetch the original with WebFetch: the company's announcement, help page or release notes,
the regulator's or government's page, or the report itself. News sites can point you to a
story but never count as the source. Openai.com and help.openai.com usually block WebFetch;
if so, use a different story rather than relying on news sites.

- Check every date, figure, price, plan name, country and quote against a fetched original.
- Find out what it means in the UK. If the source names countries, use them. If it says
  nothing, write that the company hasn't said which countries get it.
- GBP only when the source gives GBP. Never convert currencies yourself.
- **If a claim can't be checked against a fetched original, cut it. If the story falls apart
  without it, pick another story.** If nothing qualifies, publish nothing and say so.
- List every URL you fetched in `checked_sources`.

## Step 3: write the draft

Write `_pending/news/<today>.json` (UTF-8, 2-space indent, real characters like £ and
curly quotes, **no em dashes**, plain text with no HTML):

```json
{
  "date": "<today>",
  "slug": "short-lowercase-words",
  "company": "who made the news, e.g. OpenAI or National Trading Standards",
  "headline": "plain, specific, under 90 characters",
  "summary": "one or two sentences for the homepage and RSS",
  "body": ["2 to 4 short paragraphs: what happened, what it means in the UK"],
  "do_this": ["1 to 3 practical steps a reader can take; leave the list empty if none fit"],
  "source_url": "the main original source",
  "source_name": "e.g. OpenAI's announcement",
  "checked_sources": ["every URL fetched, including source_url"],
  "social": {
    "Topic": "short headline-style line, unique in the queue",
    "Caption Notes": "the full caption, short paragraphs, then 'Follow @ainofluff for more plain-English AI updates.' then a last line 'Source: <publisher>, <d Mon yyyy>.'",
    "x_text": "280 characters or fewer",
    "graphic": {"headline": "under 40 characters", "highlight": "a word or phrase from the headline",
                "lines": ["2 or 3 lines, under 40 characters each"], "source": "Source: <publisher>, <Mon yyyy>"},
    "alt_text": "one sentence describing the graphic"
  }
}
```

Reread everything against STYLE.md and revise the weakest lines. Check again that every
fact traces to `checked_sources`.

## Step 4: publish

- Run `python3 scripts/publish-news.py <today>`. It checks the draft, updates `news.html`,
  `index.html` and `feed.xml`, renders the graphic and approves the social post for 19:00.
  If it refuses, fix the draft and rerun. Never edit those files by hand.
- Open the rendered PNG in `social/` and check the text fits and reads correctly.
- Stage with `git add news.html index.html feed.xml social _pending`.
- Run `git diff --cached --name-only`. Every path must be one of those. Unstage anything else.
- Commit on `main` with the headline as the message, then push to `main`. If the push is
  rejected, `git pull --rebase` and push again. Never leave the work on another branch.

## Report

Finish with:
- if the run was skipped, why, first
- the headline, the source URL and the social slot
- stories you considered and dropped, and why
