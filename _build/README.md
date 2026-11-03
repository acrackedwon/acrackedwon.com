# _build — source pipeline for index.html

`../index.html` is a **generated, self-contained** file (images, fonts, three.js and the
3D model are all inlined). The only other deployed files are `../f1/amg.glb` and
`../f1/car.glb`, copied there by `build.py` and fetched only when the easter egg plays.
Don't hand-edit either — edit the source here and rebuild.

## Files
- `site.html` — the real editable source (HTML/CSS/JS with `{{PLACEHOLDER}}` tokens).
  Minimal single-column text layout; the 3D minifigure holds a sticky left column on PC
  and sits as a small bot in the bottom-right corner on mobile.
- `build.py` — fills every placeholder and writes `../index.html`. It fails loudly if the
  template uses a placeholder it has no value for, or if a value goes unused.
- `assets.json` — posters, logos and screenshots (complete data URIs). Only some are used now.
- `minifig/` — the rigged minifigure (a node per joint) in two outfits, assembled from
  LDraw.org parts (CC BY 2.0 — credited in the page footer). The page shows the hoodie;
  the race suit only appears in the easter egg. All motion is procedural, in `site.html`.
- Easter egg ("lights out"): five quick taps on the figure (tap 1 still waves/walks; taps
  2–5 light the start lights over the card), or typing `boxbox`. After a random hold the
  lights go out: the figure spins into the race suit (teal ring + sparks), the car
  (`car/`) pulls up, the figure hops into the cockpit and the car launches out of frame;
  then the hoodie figure drops back in. While it runs the canvas grows past the card
  (masked to fade at its edges) and the camera's FOV grows with it, so nothing jumps.
  `?debug` exposes `window.__f1` (`load`, `start`, `seek(t)`, `paused`) for stepping it.
- `car/` — the race car (see `car/README.md`): Mecabricks model by jwf1, driver removed,
  W14 livery, meshopt-compressed (`vendor/meshopt_decoder.module.js` is inlined for it).
  - `hoodie.glb` — off-white pullover hoodie, black trousers (`hoodie-guy.ldr` in the
    `acrackedwon/anything` repo, `lego-minifig/`).
  - `amg.glb` — Mercedes-AMG Petronas race suit, top and bottom, made up after the 2026
    driver suit (LDraw has no Mercedes suit newer than 2016). `gen2026.py` writes the
    `*-26.dat` parts from the official 2016 print (973pyl, 3815bpy3, 3816cpy3, 3817cpy3):
    black suit, white logos, teal Petronas accents, old Puma/BOSS marks blanked, plus new
    marks drawn as flat polygons, traced from the brands' SVGs (`logos/`, sources in
    `logos/SOURCES.md`): PETRONAS (current logo), AMG, UBS, CrowdStrike, Snapdragon, INEOS,
    signify, HPE, Microsoft, adidas; OMP in Inter Bold. Rebuild:
    Sleeves (`3818-26.dat`, `3819-26.dat`): the arm surface with a darker lower sleeve and
    the sleeve sponsors projected onto the curved arm. Rebuild (~10 min, the projection is
    brute force): `gen2026.py <ldraw/parts> . ../fonts/src/InterVariable.woff2 logos
    <anything repo>/lego-minifig`, then
    `minifig2glb.py amg-2026.ldr <ldraw lib> raw.glb` and `post.py raw.glb amg.glb`.
  - `poster-hoodie.png` — static render with the exact live framing; shown until WebGL is
    up, and kept where WebGL is unavailable. (`poster-amg.png` is no longer used.)
  - `post.py` — turns `minifig2glb.py` output into the site's GLB: lowers the head 4 LDU (no
    gap at the neck), drops the baked clips, welds vertices.
- `vendor/` — three.js r170 (`three.module.min.js`, `GLTFLoader.js`, `BufferGeometryUtils.js`;
  MIT, see `three.LICENSE`). Inlined as inert text and loaded as modules through blob URLs.
- `fonts/` — `inter.woff2` + `pretendard.woff2`, subsets cut from `fonts/src/` by
  `gen_fonts.py` (SIL OFL 1.1, see `fonts/OFL.txt`). Apple devices use the system SF Pro;
  everything else gets Inter tracked 0.01em tighter (`html.inter`, `--tk`). The Pretendard
  subset holds only the Hangul in `site.html` — `build.py` warns when it needs a rerun
  (`pip install fonttools brotli`, then `python3 _build/gen_fonts.py`).

Not used by the current design, kept for reference: `wp_*.b64.txt` + `gen_bg.py` (gradient
wallpapers), `roboto_round.b64.txt`, `icons.b64.json` + `gen_icons.py` (app icons from the
repo-root `.icns` files), and the francophones logo `../Icon.svg`.

## Rebuild
```
python3 _build/build.py
```
Then commit both the source change and the regenerated `../index.html`.
Pushing to `main` triggers `.github/workflows/deploy.yml`, which deploys to GitHub Pages.
