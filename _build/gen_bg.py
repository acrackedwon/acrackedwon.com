import numpy as np
from PIL import Image, ImageFilter
import base64, io

W, H = 1300, 2000  # portrait canvas, background-size:cover will handle any viewport

def hex2rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float64)

def lerp(a, b, t):
    t = np.clip(t, 0, 1)
    return a * (1 - t) + b * t

def make_bg(stops, band_center, band_width, band_color, band_strength,
            accent_pos, accent_color, accent_strength, accent_radius,
            vignette_strength, seed):
    """
    stops: list of (y_fraction, hex_color) top->bottom base gradient
    band_*: horizontal bright band (specular highlight), NOT diagonal
    accent_*: a brighter color-pop patch (e.g. top-right)
    vignette_strength: how much all 4 edges darken relative to center
    """
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    yf = yy / H
    xf = xx / W

    # ---- base vertical gradient ----
    img = np.zeros((H, W, 3))
    stops = sorted(stops, key=lambda s: s[0])
    for i in range(len(stops) - 1):
        y0, c0 = stops[i]
        y1, c1 = stops[i + 1]
        c0, c1 = hex2rgb(c0), hex2rgb(c1)
        mask = (yf >= y0) & (yf <= y1)
        t = (yf[mask] - y0) / max(1e-6, (y1 - y0))
        img[mask] = lerp(c0, c1, t[:, None])
    img[yf < stops[0][0]] = hex2rgb(stops[0][1])
    img[yf > stops[-1][0]] = hex2rgb(stops[-1][1])

    # ---- horizontal specular band (soft gaussian in Y only, full width) ----
    band = np.exp(-((yf - band_center) ** 2) / (2 * band_width ** 2))
    band_c = hex2rgb(band_color)
    img = img + band[..., None] * (band_c - img) * band_strength

    # ---- accent color-pop patch (radial, e.g. top-right) ----
    ax, ay = accent_pos
    dist = np.sqrt(((xf - ax) / accent_radius[0]) ** 2 + ((yf - ay) / accent_radius[1]) ** 2)
    accent = np.clip(1 - dist, 0, 1) ** 1.6
    acc_c = hex2rgb(accent_color)
    img = img + accent[..., None] * (acc_c - img) * accent_strength

    # ---- vignette: darken toward ALL edges (true photographic falloff) ----
    cx, cy = 0.5, 0.46
    edge = np.sqrt(((xf - cx) / 0.72) ** 2 + ((yf - cy) / 0.72) ** 2)
    vig = np.clip(edge - 0.35, 0, 1)
    # soften it specifically near the very top: on tall/narrow (mobile) viewports
    # background-size:cover reveals more of the top edge, and a full-strength
    # vignette up there reads as an ugly dark band — ramp the effect back in
    # over the first ~22% of the image instead of applying it at full force.
    top_protect = np.clip(yf / 0.22, 0, 1)
    vig = vig * (0.25 + 0.75 * top_protect)
    img = img * (1 - vig[..., None] * vignette_strength)

    img = np.clip(img, 0, 255).astype(np.uint8)
    pil = Image.fromarray(img, 'RGB')

    # ---- real gaussian blur for photographic softness ----
    pil = pil.filter(ImageFilter.GaussianBlur(radius=int(22 * W / 900)))

    # ---- real film grain ----
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, (H, W, 1)).repeat(3, axis=2)
    # fine grain: blend a couple of octaves for a less uniform, more organic texture
    noise2 = rng.normal(0, 1, (H // 2, W // 2, 1)).repeat(3, axis=2)
    noise2_range = noise2.max() - noise2.min()
    noise2 = np.array(Image.fromarray(((noise2 - noise2.min()) / noise2_range * 255).astype(np.uint8)[..., 0]).resize((W, H), Image.BILINEAR))
    noise2 = (noise2.astype(np.float64) - 127.5) / 127.5
    grain = 0.7 * noise[..., 0] + 0.3 * noise2
    grain_strength = 10.0  # amplitude in 0-255 space
    arr = np.array(pil).astype(np.float64)
    arr = arr + grain[..., None] * grain_strength
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, 'RGB')

# ---------- Mood A: Bleu de France ----------
bleu = make_bg(
    stops=[(0.0, '#16264a'), (0.22, '#1c3363'), (0.44, '#2748a8'), (0.66, '#3e63d9'), (1.0, '#1c3170')],
    band_center=0.40, band_width=0.055, band_color='#e8eefa', band_strength=0.55,
    accent_pos=(0.86, 0.12), accent_color='#7aa6ff', accent_strength=0.55, accent_radius=(0.30, 0.22),
    vignette_strength=0.55,
    seed=7,
)

# ---------- Mood B: Vert ----------
vert = make_bg(
    stops=[(0.0, '#25301a'), (0.22, '#324226'), (0.44, '#5c7440'), (0.66, '#8ba86a'), (1.0, '#2f3d1a')],
    band_center=0.40, band_width=0.055, band_color='#eef1e6', band_strength=0.58,
    accent_pos=(0.86, 0.12), accent_color='#a7c454', accent_strength=0.60, accent_radius=(0.30, 0.22),
    vignette_strength=0.55,
    seed=13,
)

# ---------- Mood C: Silver (메탈릭 그레이) ----------
silver = make_bg(
    stops=[(0.0, '#33363c'), (0.22, '#3f434a'), (0.44, '#6a6e75'), (0.66, '#9a9ea4'), (1.0, '#4b4e53')],
    band_center=0.40, band_width=0.055, band_color='#f3f4f6', band_strength=0.60,
    accent_pos=(0.86, 0.12), accent_color='#cfd3d8', accent_strength=0.45, accent_radius=(0.30, 0.22),
    vignette_strength=0.55,
    seed=21,
)

import os
OUT = os.path.dirname(os.path.abspath(__file__))  # write next to this script (_build/)

for name, im in [('bleu', bleu), ('vert', vert), ('silver', silver)]:
    im.save(os.path.join(OUT, f'wp_{name}.jpg'), 'JPEG', quality=84)
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=76)
    b64 = base64.b64encode(buf.getvalue()).decode()
    print(name, im.size, len(b64) // 1024, 'KB (base64)')
    with open(os.path.join(OUT, f'wp_{name}.b64.txt'), 'w') as f:
        f.write(b64)
