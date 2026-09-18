#!/usr/bin/env python3
"""
Turn the repo-root .icns app icons into the base64 PNGs that build.py inlines.

    python3 _build/gen_icons.py      # writes _build/icons.b64.json

Apple's icon grid leaves the art at ~86.7% of the tile (888 of 1024), but the
uploaded set is mixed: Keynote/Mail/Pages already carry that padding, while the
briefcase and the J fill their canvas edge to edge. Rendered at one box size
those two would read ~15% larger than the rest, so every icon is cropped to its
own alpha bounds and re-seated on the same grid.

Those two are also opaque squares — their corners are white, not transparent —
so they need the squircle cut. Rather than approximate it with a rounded
rectangle, the mask is lifted from the alpha channel of one of the genuine
Apple icons, which makes the corner curve identical by construction.
"""
from PIL import Image
import base64, io, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TILE, ART, OUT_PX = 1024, 888, 256  # 256px covers a 75px dock icon at 3x

# key -> .icns filename (repo root)
ICONS = {
    "IC_ME":       "J_AppStore_Parody.icns",
    "IC_SCHOOL":   "Pages__Default___macOS_26.2___V1rDQDsV2N_icns-7c97c4df97.icns",
    "IC_WORK":     "Briefcase_Green_AppleStyle.icns",
    "IC_PROJECTS": "Keynote__Default__LA9CMjniY1_icns-833002ae94.icns",
    "IC_CONTACT":  "Messages_macOS_Golden_Gate_ow94O6GAvP-3d83bcc95d.icns",
}


def squircle_mask(size):
    """Apple's icon silhouette, taken straight off a real Apple icon's alpha."""
    ref = Image.open(os.path.join(ROOT, ICONS["IC_PROJECTS"]))
    ref.load()
    a = ref.convert("RGBA").split()[-1]
    return a.crop(a.getbbox()).resize((size, size), Image.LANCZOS)


def normalize(path):
    im = Image.open(path)
    im.load()
    im = im.convert("RGBA")
    if im.getbbox() == (0, 0) + im.size:   # opaque square -> cut the squircle
        im.putalpha(squircle_mask(im.width))
    art = im.crop(im.getbbox())
    # longest side -> ART, keeping the aspect ratio (these are all square)
    w, h = art.size
    k = ART / max(w, h)
    art = art.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    tile = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    tile.alpha_composite(art, ((TILE - art.width) // 2, (TILE - art.height) // 2))
    return tile.resize((OUT_PX, OUT_PX), Image.LANCZOS)


def main():
    out = {}
    for key, fname in ICONS.items():
        im = normalize(os.path.join(ROOT, fname))
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode()
        out[key] = b64
        print(f"{key:12} {fname[:34]:34} {len(buf.getvalue())//1024:4d} KB -> {len(b64)//1024:4d} KB base64")
    with open(os.path.join(HERE, "icons.b64.json"), "w") as f:
        json.dump(out, f)
    print("wrote _build/icons.b64.json")


if __name__ == "__main__":
    main()
