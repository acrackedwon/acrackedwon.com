#!/usr/bin/env python3
"""
Rebuild ../index.html from the editable source in this folder.

Edit site.html (the real source), then run:

    python3 _build/build.py

It fills every {{PLACEHOLDER}} — base64 images (assets.json), the
minifigure (minifig.glb + its static poster) and three.js (vendor/) — and
writes the self-contained ../index.html that GitHub Pages serves.
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


def main():
    a = json.load(open(os.path.join(HERE, "assets.json")))

    rep = {
        # assets.json values are complete data URIs
        "LOGO_NEW": a["logo_new"], "LOGO_OLD": a["logo_old"],
        "LYS_CLEAN": a["lys_clean"], "CONF": a["CONF"], "LEX": a["LEX"],
        # 3D minifigure
        "MINIFIG_POSTER": b64file("minifig_poster.png"),
        "MINIFIG_GLB": b64file("minifig.glb"),
        "THREE_JS": read("vendor/three.module.min.js"),
        "BGU_JS": read("vendor/BufferGeometryUtils.js"),
        "GLTF_JS": read("vendor/GLTFLoader.js"),
        # web fonts (subsets cut by gen_fonts.py)
        "INTER_WOFF2": b64file("fonts/inter.woff2"),
        "PRETENDARD_WOFF2": b64file("fonts/pretendard.woff2"),
    }
    rep.update({"NP%d" % i: a["NP%d" % i] for i in range(1, 11)})

    for k in ("THREE_JS", "BGU_JS", "GLTF_JS"):
        assert "</script" not in rep[k].lower(), k + " would close its <script> early"

    html = read(TEMPLATE)
    have = set(read("fonts/pretendard-chars.txt").strip())
    new = {c for c in html if 0xAC00 <= ord(c) <= 0xD7A3} - have
    if new:
        print("warning: Hangul not in the Pretendard subset (rerun gen_fonts.py):", "".join(sorted(new)))
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
        "<meta name=\"theme-color\" content=\"#f2f2f0\">\n"
        "<title>Jiwon Shin</title>\n"
        "<meta name=\"description\" content=\"Jiwon Shin — designer, operator. French at Kyung Hee. Small brands, end to end.\">\n"
        "</head>\n<body>\n" + body + "\n</body>\n</html>\n"
    )
    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    print("wrote", out, len(doc.encode()) // 1024, "KB")


if __name__ == "__main__":
    main()
