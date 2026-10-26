#!/usr/bin/env python3
"""
Cut the two web fonts the site embeds down to what it actually uses.

    python3 -m pip install fonttools brotli
    python3 _build/gen_fonts.py

- fonts/inter.woff2       Inter (variable, opsz 14-32 so large text gets
                          the Display cut automatically), weights 400-600,
                          Latin only.
- fonts/pretendard.woff2  Pretendard (variable), weights 400-600, only the
                          Hangul syllables that appear in site.html.

Rerun after adding new Korean text; build.py warns when it is needed.
Both fonts are SIL OFL 1.1 (fonts/OFL.txt); sources are in fonts/src.
"""
import os, re
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts")

LATIN = [*range(0x20, 0x7F), *range(0xA0, 0x100), 0x131, 0x152, 0x153,
         0x2013, 0x2014, 0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x2022,
         0x2026, 0x2032, 0x2033, 0x20AC, 0x2122, 0x2190, 0x2191, 0x2192,
         0x2193, 0x2197, 0x2212, 0x2264, 0x2265]
FEATURES = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk", "tnum", "case"]


def hangul():
    s = open(os.path.join(HERE, "site.html"), encoding="utf-8").read()
    return sorted({c for c in s if 0xAC00 <= ord(c) <= 0xD7A3})


def cut(src, dst, unicodes, axes):
    font = TTFont(os.path.join(F, "src", src))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = FEATURES
    opts.name_IDs = ["*"]          # keep copyright/licence names (OFL)
    opts.notdef_outline = True
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=unicodes)
    sub.subset(font)
    font = instancer.instantiateVariableFont(font, axes)
    out = os.path.join(F, dst)
    font.flavor = "woff2"
    font.save(out)
    print(f"{dst}: {os.path.getsize(out):,} bytes")


def main():
    cut("InterVariable.woff2", "inter.woff2", LATIN,
        {"wght": (400, 600), "opsz": (14, 32)})
    chars = hangul()
    cut("PretendardVariable.woff2", "pretendard.woff2",
        [ord(c) for c in chars], {"wght": (400, 600)})
    with open(os.path.join(F, "pretendard-chars.txt"), "w", encoding="utf-8") as f:
        f.write("".join(chars) + "\n")


if __name__ == "__main__":
    main()
