#!/usr/bin/env python3
"""
Rebuild ../index.html from the editable source in this folder.

Edit site.html (the real source), then run:

    python3 _build/build.py

It fills every {{PLACEHOLDER}} — base64 images (assets.json), the three
background wallpapers (wp_*.b64.txt), the embedded Roboto Round fallback
font, the tab-bar icons (icons.b64.json), the francophones icon (built from
../Icon.svg), the minifigure (minifig.glb + its static poster) and three.js
(vendor/) — and writes the self-contained ../index.html that GitHub Pages
serves.
"""
import base64, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = "site.html"


def read(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as f:
        return f.read()


def b64file(name):
    with open(os.path.join(HERE, name), "rb") as f:
        return base64.b64encode(f.read()).decode()


def franco_icon():
    # fleur-de-lys path reused inside a luminance mask over a rotated taegeuk
    raw = open(os.path.join(ROOT, "Icon.svg"), encoding="utf-8").read()
    d = re.search(r'<path id="fleur-de-lys" d="([^"]+)"', raw).group(1)
    return (
        f'<svg class="franco" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2500 2500" '
        f'role="img" aria-label="Francophones Korea logo"><defs><path id="fdl" d="{d}"/>'
        f'<mask id="fdlmask" maskUnits="userSpaceOnUse" x="0" y="0" width="2500" height="2500" '
        f'mask-type="luminance"><rect width="2500" height="2500" fill="#fff"/>'
        f'<use href="#fdl" transform="translate(490 208) scale(2.848880597)" fill="#000"/></mask></defs>'
        f'<g mask="url(#fdlmask)"><g transform="translate(1250 1250) scale(52.0833333)">'
        f'<g transform="rotate(33.69006752598)">'
        f'<path fill="#cd2e3a" d="M12 0a18 18 0 11-36 0 24 24 0 1148 0"/>'
        f'<path fill="#0047a0" d="M0 0a12 12 0 1124 0 24 24 0 11-48 0 12 12 0 1024 0"/>'
        f'</g></g></g></svg>'
    )


def main():
    a = json.load(open(os.path.join(HERE, "assets.json")))
    icons = json.load(open(os.path.join(HERE, "icons.b64.json")))

    rep = {
        "ROBOTO_ROUND": read("roboto_round.b64.txt").strip(),
        "WP_BLEU": read("wp_bleu.b64.txt").strip(),
        "WP_VERT": read("wp_vert.b64.txt").strip(),
        "WP_SILVER": read("wp_silver.b64.txt").strip(),
        "FRANCO_ICON": franco_icon(),
        # assets.json values are complete data URIs
        "LOGO_NEW": a["logo_new"], "LOGO_OLD": a["logo_old"], "NAVER": a["naver"],
        "LYS_CLEAN": a["lys_clean"], "PMA_CLEAN": a["pma_clean"], "APRESDOCX": a["apresdocx"],
        "CONF": a["CONF"], "LEX": a["LEX"],
        # 3D minifigure
        "MINIFIG_POSTER": b64file("minifig_poster.png"),
        "MINIFIG_GLB": b64file("minifig.glb"),
        "THREE_JS": read("vendor/three.module.min.js"),
        "BGU_JS": read("vendor/BufferGeometryUtils.js"),
        "GLTF_JS": read("vendor/GLTFLoader.js"),
    }
    rep.update({k: v for k, v in icons.items()})                 # IC_* (plain base64)
    rep.update({"NP%d" % i: a["NP%d" % i] for i in range(1, 11)})

    for k in ("THREE_JS", "BGU_JS", "GLTF_JS"):
        assert "</script" not in rep[k].lower(), k + " would close its <script> early"

    html = read(TEMPLATE)
    used = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", html))
    missing = used - rep.keys()
    assert not missing, "no value for placeholder(s): " + ", ".join(sorted(missing))
    unused = rep.keys() - used
    assert not unused, "value(s) not used by the template: " + ", ".join(sorted(unused))

    # One pass, so inserted content (e.g. three.js) is never rescanned for {{…}}.
    html = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: rep[m.group(1)], html)

    # The template is authored as page content (it starts at <title>); wrap it in a
    # proper document — without <meta name="viewport"> mobile browsers would fall
    # back to a ~980px desktop layout.
    body = re.sub(r"^<title>.*?</title>\s*", "", html, count=1, flags=re.DOTALL)
    doc = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
        "<title>Jiwon Shin</title>\n"
        "<meta name=\"description\" content=\"Jiwon Shin — French major at Kyung Hee who designs, builds, and runs small brands, end to end.\">\n"
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )
    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", out, len(doc.encode()) // 1024, "KB")


if __name__ == "__main__":
    main()
