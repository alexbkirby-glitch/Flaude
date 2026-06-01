# Flaude

A text adventure disguised as an AI assistant.

**[Play it →](https://your-username.github.io/flaude)**

---

## Deploying to GitHub Pages

1. **Create a new repo** on GitHub — call it `flaude` (or anything you like).

2. **Upload the files** — drag `index.html`, `README.md`, and `.nojekyll` into the root of the repo. The `.nojekyll` file is important; it stops GitHub from trying to process the site with Jekyll.

3. **Enable GitHub Pages** — go to your repo's **Settings → Pages**, set the source to **Deploy from a branch**, choose `main`, folder `/root`, and hit Save.

4. **Wait a minute** — GitHub will build and publish the site. The URL will be `https://your-username.github.io/flaude`.

---

## Development

The game is a single self-contained HTML file. To edit it, just open `index.html` in a text editor — everything is in there.

If you need to regenerate `index.html` from scratch (e.g. after swapping the logo), run the build script:

```bash
python3 build_flaude.py
```

This reads `logo_small_b64.txt` (the embedded logo, not included here — extract it from the `LOGO` constant in `index.html` if needed) and writes a fresh `index.html`. For most changes, editing `index.html` directly is simpler.

---

## How to add story scenes

Open `index.html` and find the `BREAK_TYPES` array and `WIN_SEQUENCE`. Breaks use regex patterns — each one triggers once and escalates the glitch level. The win condition fires when the player says a variant of *"I'm wrong"*.

To add new keywords to a break, extend its `pattern` regex. To change a response, edit the `response` string directly.
