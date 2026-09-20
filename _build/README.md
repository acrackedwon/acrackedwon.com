# _build — source pipeline for index.html

`../index.html` is a **generated, self-contained** file (all images + fonts are
inlined as base64, so it deploys with no other assets). Don't hand-edit it —
edit the source here and rebuild.

## Files
- `mockup_b_template.html` — the real editable source (HTML/CSS/JS with `{{PLACEHOLDER}}` tokens). Structure: wallpaper → macOS-style dock (5 app icons) → on click the dock drops to the bottom and becomes WebGL glass, and that section's window (`.win`, Apple grouped-inset lists) zooms open above it.
- `build.py` — injects every placeholder and writes `../index.html`.
- `assets.json` — base64 for logos, posters, screenshots, the aprèsdocx wordmark, etc.
- `wp_bleu.b64.txt` / `wp_vert.b64.txt` / `wp_silver.b64.txt` — the three background wallpapers (base64 JPEG).
- `roboto_round.b64.txt` — the embedded Roboto Round web-font (SF Pro Rounded fallback for non-Apple devices), base64 woff2.
- `icons.b64.json` — the five dock icons (base64 PNG), built from the repo-root `.icns` files.
- `gen_icons.py` — regenerates `icons.b64.json`. Only needed if an icon changes.
- `gen_bg.py` — regenerates the background wallpapers (PIL + numpy). Only needed if you change a mood.
- `../Icon.svg` (repo root) — the francophones logo; `build.py` builds the masked SVG from it.

## Rebuild
```
python3 _build/build.py
```
Then commit both the source change and the regenerated `../index.html`.
Pushing to `main` triggers `.github/workflows/deploy.yml`, which deploys to GitHub Pages.

## Regenerate dock icons (rarely)
```
pip install pillow
python3 _build/gen_icons.py   # reads ../*.icns -> icons.b64.json
python3 _build/build.py
```

## Regenerate backgrounds (rarely)
```
pip install pillow numpy
python3 _build/gen_bg.py      # writes wp_*.jpg + wp_*.b64.txt into _build/
python3 _build/build.py
```
