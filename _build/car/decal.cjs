// node decal.cjs probe rays.json | build specs.json out-prefix [views...] [--export out.glb]
const { chromium } = require('playwright'); const fs = require('fs');
const [mode, file, out, ...rest] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader'] }); const p = await b.newPage({ viewport: { width: 1400, height: 800 } });
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log(m.text().slice(0, 300)); });
  await p.goto('http://127.0.0.1:8771/w15tool/decal.html?f=' + (process.env.CAR || 'out/w15-nodriver.glb') + ''); await p.waitForFunction(() => window.done, { timeout: 120000 });
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  if (mode === 'probe') { const res = await p.evaluate(r => probe(r), data); data.forEach((r, i) => console.log(JSON.stringify(r), '->', JSON.stringify(res[i]))); }
  else {
    const log = await p.evaluate(s => build(s), data); log.forEach(l => console.log(JSON.stringify(l)));
    let ex = rest.indexOf('--export'); const views = ex >= 0 ? rest.slice(0, ex) : rest;
    for (const v of views) { const [az, el, z, t] = v.split('/'); await p.evaluate(([a, e, zz, tt]) => shot(+a, +e, +zz, tt && tt.split(',').map(Number)), [az, el, z, t]); await p.screenshot({ path: `${out}-${v.replace(/[^0-9a-z-]+/gi, '_')}.png` }); }
    if (ex >= 0) { const b64 = await p.evaluate(() => exportGLB()); fs.writeFileSync(rest[ex + 1], Buffer.from(b64, 'base64')); console.log('wrote', rest[ex + 1]); }
  }
  await b.close();
})();
