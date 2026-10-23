# _build — source pipeline for index.html

`../index.html` is a **generated, self-contained** file (images, fonts, three.js and the
3D model are all inlined, so it deploys with no other assets). Don't hand-edit it —
edit the source here and rebuild.

## Files
- `site.html` — the real editable source (HTML/CSS/JS with `{{PLACEHOLDER}}` tokens).
  Minimal single-column text layout; the 3D minifigure holds a sticky left column on PC
  and sits as a small bot in the bottom-right corner on mobile.
- `build.py` — fills every placeholder and writes `../index.html`. It fails loudly if the
  template uses a placeholder it has no value for, or if a value goes unused.
- `assets.json` — posters, logos and screenshots (complete data URIs). Only some are used now.
- `minifig.glb` — the rigged minifigure (a node per joint), assembled from LDraw.org parts
  (CC BY 2.0 — credited in the page footer). The wave is animated in `site.html`, not in the GLB.
- `minifig_poster.png` — static render with the exact live framing; shown until WebGL is up,
  and kept where WebGL is unavailable.
- `vendor/` — three.js r170 (`three.module.min.js`, `GLTFLoader.js`, `BufferGeometryUtils.js`;
  MIT, see `three.LICENSE`). Inlined as inert text and loaded as modules through blob URLs.

Not used by the current design, kept for reference: `wp_*.b64.txt` + `gen_bg.py` (gradient
wallpapers), `roboto_round.b64.txt`, `icons.b64.json` + `gen_icons.py` (app icons from the
repo-root `.icns` files), and the francophones logo `../Icon.svg`.

## Rebuild
```
python3 _build/build.py
```
Then commit both the source change and the regenerated `../index.html`.
Pushing to `main` triggers `.github/workflows/deploy.yml`, which deploys to GitHub Pages.
