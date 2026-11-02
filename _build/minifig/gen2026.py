"""Mercedes-AMG Petronas 2026-style race suit for the minifig, as LDraw parts.

Starts from the official 2016 print (973pyl, 3815bpy3, 3816cpy3, 3817cpy3),
recolours it (black suit, white logos, teal Petronas accents, the old Puma
and BOSS marks hidden, seams toned down), then lays new marks over the front
as flat polygons a hair in front of the surface: AMG, INEOS, HPE, Microsoft
(squares + word), the teal line under PETRONAS, adidas stripes on the
shoulders and the adidas mark at the hip, OMP, teal shoulder sweeps; and
mirrors the teal side panel onto the other leg. Lettering is Inter Bold,
outlined with fontTools and triangulated with earcut: close to, not the same
as, the brands' own type.
"""
import sys, math
from pathlib import Path
import numpy as np
import mapbox_earcut as earcut
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.recordingPen import DecomposingRecordingPen

LIB = Path(sys.argv[1])            # ldraw/parts
OUT = Path(sys.argv[2])
FONT = sys.argv[3]
TEAL, DARK, WHITE, BASE, BLACK = '0x200A19B', '0x22A2E33', '15', '16', '0'
Z = -10.08                         # just in front of the torso's front face (z = -10)

def lines(name):
    return (LIB / name).read_text(errors='replace').replace('\r', '').splitlines()

def recol(line, mapping):
    t = line.split()
    if t and t[0] in '12345' and len(t) > 1 and t[1] in mapping:
        t[1] = mapping[t[1]]; return ' '.join(t)
    return line

# ---------------- lettering ----------------
font = instancer.instantiateVariableFont(TTFont(FONT), {'wght': 700, 'opsz': 32})
gs, cmap, hmtx = font.getGlyphSet(), font.getBestCmap(), font['hmtx']
CAP = font['OS/2'].sCapHeight

def quad(p0, p1, p2, n=6):
    return [((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0], (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]) for t in (i / n for i in range(1, n + 1))]
def cubic(p0, p1, p2, p3, n=8):
    return [tuple((1-t)**3*a + 3*(1-t)**2*t*b + 3*(1-t)*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3)) for t in (i / n for i in range(1, n + 1))]

def glyph_contours(ch):
    pen = DecomposingRecordingPen(gs); gs[cmap[ord(ch)]].draw(pen)
    out, cur = [], []
    for op, args in pen.value:
        if op == 'moveTo': cur = [args[0]]
        elif op == 'lineTo': cur.append(args[0])
        elif op == 'qCurveTo':
            pts = list(args); start = cur[-1]
            for i in range(len(pts) - 1):
                on = pts[-1] if i == len(pts) - 2 else ((pts[i][0] + pts[i+1][0]) / 2, (pts[i][1] + pts[i+1][1]) / 2)
                cur += quad(start, pts[i], on); start = on
        elif op == 'curveTo': cur += cubic(cur[-1], *args)
        elif op in ('closePath', 'endPath'):
            if len(cur) > 2: out.append(cur)
            cur = []
    return out, hmtx[cmap[ord(ch)]][0]

def area(c): return 0.5 * sum(a[0]*b[1] - b[0]*a[1] for a, b in zip(c, c[1:] + c[:1]))
def inside(p, c):
    x, y, r = p[0], p[1], False
    for (x1, y1), (x2, y2) in zip(c, c[1:] + c[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): r = not r
    return r

def fill(contours):
    """contours (with holes) -> triangles, grouping holes into their outer ring."""
    tris = []
    depth = [sum(inside(c[0], o) for o in contours if o is not c) for c in contours]
    for i, c in enumerate(contours):
        if depth[i] % 2: continue
        holes = [h for j, h in enumerate(contours) if depth[j] == depth[i] + 1 and inside(h[0], c)]
        rings = [c] + holes
        verts = np.array([p for r in rings for p in r], dtype=np.float64)
        ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
        idx = earcut.triangulate_float64(verts, ends)
        tris += [tuple(map(tuple, verts[idx[k:k+3]])) for k in range(0, len(idx), 3)]
    return tris

def text(s, cx, base_y, cap, col, skew=0.0, track=0.0):
    """Centered text; base_y is the baseline in LDraw y (down), cap = cap height in LDU."""
    k = cap / CAP; x = 0.0; allc = []
    for ch in s:
        if ch == ' ': x += hmtx[cmap[32]][0] + track / k; continue
        cs, adv = glyph_contours(ch)
        allc += [[(px + x, py) for px, py in c] for c in cs]; x += adv + track / k
    w = (x - track / k) * k
    tris = fill(allc)
    return [(col, [(cx - w / 2 + px * k + py * k * skew, base_y - py * k) for px, py in t]) for t in tris], w

def rect(x0, y0, x1, y1, col): return [(col, [(x0, y0), (x1, y0), (x1, y1)]), (col, [(x0, y0), (x1, y1), (x0, y1)])]
def poly4(a, b, c, d, col): return [(col, [a, b, c]), (col, [a, c, d])]
def band(p, q, w, col):
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
    return poly4((p[0]+nx, p[1]+ny), (q[0]+nx, q[1]+ny), (q[0]-nx, q[1]-ny), (p[0]-nx, p[1]-ny), col)

def emit(tris):
    out = []
    for col, t in tris:
        (x1, y1), (x2, y2), (x3, y3) = t
        if (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1) > 0:      # same winding for every decal
            (x2, y2), (x3, y3) = (x3, y3), (x2, y2)
        out.append(f'3 {col} {x1:.3f} {y1:.3f} {Z} {x2:.3f} {y2:.3f} {Z} {x3:.3f} {y3:.3f} {Z}')
    return out

# ---------------- torso ----------------
src = lines('973pyl.dat')
dst = []
for n, line in enumerate(src, 1):
    t = line.split()
    if n == 1: line = '0 Minifig Torso Race Suit Mercedes-AMG Petronas 2026-style (black; from 973pyl, recoloured + new marks)'
    elif n == 2: line = '0 Name: 973pyl-26.dat'
    elif t and t[0] == '1':
        ref = t[-1]
        if ref == 's\\973pyls01.dat': line = ' '.join(t[:-1] + ['973pyls01-26.dat'])          # BOSS, hidden
        elif ref == 'logo-petronas.dat': line = recol(line, {'15': BASE})
        elif ref == 'logo-petronas-inner.dat': line = recol(line, {'2': TEAL})
        elif ref.startswith('logo-ubs'): line = recol(line, {'0': BASE})   # stitched into the surface: blank it, redraw lower down
        else: line = recol(line, {'0': WHITE if ref.startswith('logo-') else DARK})
    elif 57 <= n <= 179 or 697 <= n <= 933: line = recol(line, {'0': BASE})                 # Puma logos, gone
    elif 934 <= n <= 1070: line = recol(line, {'0': WHITE})                                  # PETRONAS
    elif (180 <= n <= 290) or (1071 <= n <= 1274): line = recol(line, {'0': DARK, '71': DARK, '72': DARK})  # collar, zip, seams: quiet
    dst.append(line)

marks = []
marks += text('AMG', -6.4, 13.6, 0.85, WHITE, skew=0.25)[0]
marks += rect(-10.3, 13.1, -8.4, 13.33, WHITE) + rect(-10.55, 12.7, -8.65, 12.93, WHITE)  # AMG speed lines
marks += text('UBS', -6.6, 15.75, 1.0, WHITE, track=0.05)[0]
marks += text('INEOS', 8.35, 14.3, 1.05, WHITE, track=0.12)[0]
marks += text('HPE', 8.35, 16.1, 1.05, WHITE)[0]
marks += rect(-9.0, 22.15, 9.0, 22.5, TEAL)                                             # line under PETRONAS
mt, mw = text('Microsoft', 0, 25.6, 1.75, WHITE)
sq, gap = 1.05, 0.18
gx = -(mw + 2 * sq + gap + 0.9) / 2                                                   # logo + word, centred together
for i, j in ((0, 0), (1, 0), (0, 1), (1, 1)):
    marks += rect(gx + i * (sq + gap), 23.45 + j * (sq + gap), gx + i * (sq + gap) + sq, 23.45 + j * (sq + gap) + sq, WHITE)
marks += [(c, [(x + gx + 2 * sq + gap + 0.9 + mw / 2, y) for x, y in t]) for c, t in mt]
for s in (-1, 1):                                                                     # shoulders: adidas stripes, teal sweep
    for k in range(3):
        y = 0.45 + k * 0.7
        marks += rect(min(s * 7.4, s * 11.6), y, max(s * 7.4, s * 11.6), y + 0.38, WHITE)
    marks += band((s * 5.6, 2.9), (s * 13.2, 4.6), 0.42, TEAL)
for k in range(3):                                                                    # adidas mark, left hip
    x0 = 7.6 + k * 0.62; h = 0.8 + k * 0.45
    marks += poly4((x0, 29.6), (x0 + 0.45, 29.6), (x0 + 0.45 + h * 0.55, 29.6 - h), (x0 + h * 0.55, 29.6 - h), WHITE)
marks += text('OMP', -8.6, 29.5, 0.95, WHITE, skew=0.2)[0]
dst += ['', '0 // 2026 marks (decals in front of the front face)'] + emit(marks)
(OUT / '973pyl-26.dat').write_text('\n'.join(dst) + '\n')

boss = [recol(l, {c: BASE for c in ('0', '15', '2', '71', '72')}) for l in lines('s/973pyls01.dat')]
boss[0] = '0 ~BOSS patch blanked to the suit colour'; boss[1] = '0 Name: 973pyls01-26.dat'
(OUT / '973pyls01-26.dat').write_text('\n'.join(boss) + '\n')

# ---------------- hips and legs ----------------
hips = [recol(l, {'0': BASE, '71': DARK}) for l in lines('3815bpy3.dat')]   # Puma gone
hips[0] = '0 Minifig Hips Racing Suit 2026-style'; (OUT / '3815bpy3-26.dat').write_text('\n'.join(hips) + '\n')
legr = [recol(l, {'2': TEAL, '0': WHITE, '71': DARK}) for l in lines('3816cpy3.dat')]
legr[0] = '0 Minifig Leg Right Racing Suit 2026-style'; (OUT / '3816cpy3-26.dat').write_text('\n'.join(legr) + '\n')
legl = [recol(l, {'71': DARK}) for l in lines('3817cpy3.dat')]
legl[0] = '0 Minifig Leg Left Racing Suit 2026-style (teal panel mirrored from the right leg)'
mirror = []
for l in lines('3816cpy3.dat'):
    t = l.split()
    if t and t[0] in '34' and t[1] == '2':
        n = int(t[0]); p = np.array(t[2:2 + 3 * n], float).reshape(n, 3); p[:, 0] *= -1
        nrm = np.cross(p[1] - p[0], p[2] - p[0]); nrm /= np.linalg.norm(nrm) + 1e-12
        out = p.mean(0) - np.array([10.0, p.mean(0)[1], 0.0])         # away from the left leg's axis
        if nrm @ out < 0: nrm = -nrm
        p = p + nrm * 0.15
        mirror.append(f'{n} {TEAL} ' + ' '.join(f'{v:.4f}' for v in p[::-1].reshape(-1)))
(OUT / '3817cpy3-26.dat').write_text('\n'.join(legl + ['0 // teal side panel, mirrored'] + mirror) + '\n')
print('ok', len(marks), 'decal triangles,', len(mirror), 'mirrored')
