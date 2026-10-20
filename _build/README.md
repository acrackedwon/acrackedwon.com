# _build — source pipeline for index.html

`../index.html` is a **generated, self-contained** file (images, fonts, three.js and the
3D model are all inlined, so it deploys with no other assets). Don't hand-edit it —
edit the source here and rebuild.

## Files
- `site.html` — the real editable source (HTML/CSS/JS with `{{PLACEHOLDER}}` tokens).
  Hero tilt card with a live 3D minifigure, one bento section per subject, a floating
  glass tab bar.
- `build.py` — fills every placeholder and writes `../index.html`. It fails loudly if the
  template uses a placeholder it has no value for, or if a value goes unused.
- `assets.json` — logos, posters, screenshots, the aprèsdocx wordmark (complete data URIs).
- `wp_bleu.b64.txt` / `wp_vert.b64.txt` / `wp_silver.b64.txt` — the three background wallpapers.
- `roboto_round.b64.txt` — embedded Roboto Round (SF Pro Rounded fallback off Apple devices).
- `icons.b64.json` — the five tab-bar app icons, built by `gen_icons.py` from the repo-root `.icns` files.
- `minifig.glb` — the rigged minifigure (nodes per joint, `Walk` / `Wave` clips), assembled
  from LDraw.org parts (CC BY 2.0 — credited in the page footer).
- `minifig_poster.png` — static render with the exact live framing; shown until WebGL is up,
  and kept where WebGL is unavailable.
- `vendor/` — three.js r170 (`three.module.min.js`, `GLTFLoader.js`, `BufferGeometryUtils.js`;
  MIT, see `three.LICENSE`). Inlined as inert text and loaded as modules through blob URLs.
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
