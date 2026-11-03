// Logo rasteriser: each logo -> canvas (transparent bg), trimmed to its ink.
const LOG = 'logos/'; // + InterVariable.woff2 copied from ../fonts/src
export const C = { white: '#f2f2f2', silver: '#b9bec4', teal: '#00a19b', red: '#c8102e', ineosRed: '#b5121b' };
const H = 160; // raster height (px) of a logo's ink

await new FontFace('InterB', `url(${LOG}InterVariable.woff2)`, { weight: '100 900' }).load().then(f => document.fonts.add(f));

async function svgImg(file) {
  const txt = await (await fetch(LOG + file)).text();
  const img = new Image(); img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(txt)));
  await img.decode(); return img;
}
function canvas(w, h) { const c = document.createElement('canvas'); c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h)); return c; }
function trim(c, pad = 6) {
  const x = c.getContext('2d'), d = x.getImageData(0, 0, c.width, c.height).data;
  let x0 = c.width, y0 = c.height, x1 = -1, y1 = -1;
  for (let y = 0; y < c.height; y++) for (let i = 0; i < c.width; i++) if (d[(y * c.width + i) * 4 + 3] > 8) { if (i < x0) x0 = i; if (i > x1) x1 = i; if (y < y0) y0 = y; if (y > y1) y1 = y; }
  const o = canvas(x1 - x0 + 1 + pad * 2, y1 - y0 + 1 + pad * 2); o.getContext('2d').drawImage(c, x0 - pad, y0 - pad, x1 - x0 + 1 + pad * 2, y1 - y0 + 1 + pad * 2, 0, 0, x1 - x0 + 1 + pad * 2, y1 - y0 + 1 + pad * 2); return o;
}
// draw an SVG big, keep only "ink" (dark-or-coloured pixels, or any opaque pixel if keepAll), recolour
async function svgInk(file, colour, { scale = 4, crop = null, inkTest = null } = {}) {
  const img = await svgImg(file);
  const w = img.naturalWidth || 400, h = img.naturalHeight || 120;
  const k = (H * scale) / h; const c = canvas(w * k, h * k); const x = c.getContext('2d', { willReadFrequently: true });
  x.drawImage(img, 0, 0, c.width, c.height);
  const id = x.getImageData(0, 0, c.width, c.height), d = id.data;
  const [R, G, B] = hex(colour);
  for (let i = 0; i < d.length; i += 4) {
    const px = (i / 4) % c.width, py = Math.floor(i / 4 / c.width);
    let a = d[i + 3] / 255;
    if (inkTest) a *= inkTest(d[i], d[i + 1], d[i + 2]);
    if (crop && (px < crop[0] * c.width || px > crop[2] * c.width || py < crop[1] * c.height || py > crop[3] * c.height)) a = 0;
    d[i] = R; d[i + 1] = G; d[i + 2] = B; d[i + 3] = Math.round(a * 255);
  }
  x.putImageData(id, 0, 0);
  const t = trim(c, 0); const o = canvas(t.width * H / t.height, H); o.getContext('2d').drawImage(t, 0, 0, o.width, o.height); return o;
}
function hex(s) { return [1, 3, 5].map(i => parseInt(s.slice(i, i + 2), 16)); }
function text(str, colour, { weight = 800, track = 0 } = {}) {
  const c = canvas(H * str.length * 0.9 + 40, H * 1.6), x = c.getContext('2d');
  x.font = `${weight} ${H * 1.36}px InterB`; x.fillStyle = colour; x.textBaseline = 'alphabetic';
  if (track) x.letterSpacing = track + 'px';
  x.fillText(str, 10, H * 1.3); return trim(c, 0);
}
function row(parts, gap = 0.25, h = H) { // lay canvases side by side, vertically centred, scaled to height h each (or own scale)
  const sc = parts.map(p => (p.h || h) / p.c.height), w = parts.reduce((s, p, i) => s + p.c.width * sc[i], 0) + gap * h * (parts.length - 1);
  const c = canvas(w, h); const x = c.getContext('2d'); let px = 0;
  parts.forEach((p, i) => { const pw = p.c.width * sc[i], ph = p.c.height * sc[i]; x.drawImage(p.c, px, (h - ph) / 2, pw, ph); px += pw + gap * h; });
  return c;
}
function badge(inner, bg, padX = 0.35, padY = 0.32, r = 0.18) {
  const h = inner.height * (1 + padY * 2), w = inner.width + inner.height * padX * 2, c = canvas(w, h), x = c.getContext('2d');
  x.fillStyle = bg; x.beginPath(); x.roundRect(0, 0, w, h, h * r); x.fill();
  x.drawImage(inner, inner.height * padX, inner.height * padY); return c;
}
export function star(colour, { ring = true } = {}) {
  const s = 512, c = canvas(s, s), x = c.getContext('2d'), R = s / 2 - 8, cx = s / 2, cy = s / 2;
  x.fillStyle = x.strokeStyle = colour;
  if (ring) { x.lineWidth = R * 0.085; x.beginPath(); x.arc(cx, cy, R - x.lineWidth / 2, 0, Math.PI * 2); x.stroke(); }
  const r = ring ? R * 0.93 : R, wv = 0.21; // three points
  x.beginPath();
  for (let k = 0; k < 3; k++) {
    const a = -Math.PI / 2 + k * 2 * Math.PI / 3, b1 = a + Math.PI / 3, b2 = a - Math.PI / 3;
    x.moveTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r);
    x.lineTo(cx + Math.cos(b1) * r * wv, cy + Math.sin(b1) * r * wv);
    x.lineTo(cx, cy);
    x.lineTo(cx + Math.cos(b2) * r * wv, cy + Math.sin(b2) * r * wv);
    x.closePath();
  }
  x.fill(); return c;
}
const dark = (r, g, b) => (r + g + b) / 3 < 140 ? 1 : 0;

export async function buildLogos() {
  const L = {};
  // PETRONAS: wordmark only (right of the emblem) in white; the emblem in teal
  L.petronas = await svgInk('pw-1.svg', C.white, { crop: [0.307, 0.36, 1, 0.63] });
  L.petronasFull = row([{ c: await svgInk('pw-1.svg', C.teal, { crop: [0, 0, 0.303, 1] }), h: H * 1.9 }, { c: L.petronas }], 0.3, H * 1.9);
  const ineosW = await svgInk('k-ineos.svg', C.white);
  L.ineos = badge(ineosW, C.ineosRed);
  L.ineosWhite = ineosW;
  L.amg = await svgInk('amg.svg', C.white, { scale: 30 });
  const tvIcon = await svgInk('teamviewer.svg', C.white, { scale: 1 });
  L.teamviewer = row([{ c: tvIcon, h: H * 1.05 }, { c: text('TeamViewer', C.white, { weight: 700 }) }], 0.22, H * 1.05);
  L.snapdragon = row([{ c: await svgInk('snapdragon.svg', C.white, { scale: 1 }), h: H * 1.25 }, { c: text('Snapdragon', C.white, { weight: 600 }) }], 0.2, H * 1.25);
  L.crowdstrike = await svgInk('d-crowdstrike.svg', C.white, { inkTest: dark });
  L.amd = await svgInk('si2-amd.svg', C.white, { scale: 12 });
  L.solera = text('SOLERA', C.white, { weight: 800, track: 6 });
  L.iwc = await svgInk('sl-iwc.svg', C.white, { inkTest: (r, g, b) => 1, crop: [0, 0, 1, 0.62] });
  L.einhell = text('Einhell', C.white, { weight: 800 });
  L.star = star(C.silver);
  L.starW = star(C.white);
  L.starBare = star(C.silver, { ring: false });
  L.starDark = star('#24272b');
  L.amgDark = await svgInk('amg.svg', '#1d2023', { scale: 30 });
  L.petronasEmblem = await svgInk('pw-1.svg', C.teal, { crop: [0, 0, 0.303, 1] });
  L.n63 = text('63', '#e0e3e6', { weight: 800 });
  return L;
}

// shelf-pack logos into one atlas; returns {canvas, rects: name -> [u0, v0, u1, v1] (v from bottom)}
export function atlas(L, size = 2048, rowH = 176) {
  const c = canvas(size, size), x = c.getContext('2d'), rects = {};
  let px = 0, py = 0, pad = 10;
  for (const [k, im] of Object.entries(L)) {
    let h = rowH - pad * 2, w = im.width * h / im.height;
    if (w > size - pad * 2) { w = size - pad * 2; h = im.height * w / im.width; }
    if (px + w + pad * 2 > size) { px = 0; py += rowH; }
    x.drawImage(im, px + pad, py + pad, w, h);
    rects[k] = { r: [(px + pad) / size, 1 - (py + pad + h) / size, (px + pad + w) / size, 1 - (py + pad) / size], aspect: w / h };
    px += w + pad * 2;
  }
  return { canvas: c, rects };
}
