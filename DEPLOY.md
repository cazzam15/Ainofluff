# Deploy checklist

Run through this before every push to `main`.

- [ ] `git pull` first. The cloud routines commit to this repo too.
- [ ] Lowercase filenames only.
- [ ] No `.nojekyll` file. `_pending/` relies on Jekyll to stay off the live site.
- [ ] Every `href` points to a file that exists.
- [ ] The page loads on the live site (https://www.ainofluff.co.uk) after pushing.
