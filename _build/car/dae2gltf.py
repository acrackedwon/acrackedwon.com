# Mecabricks Collada -> glTF (merged by material, base colour + decal baked into opaque textures)
# usage: python3 -I dae2gltf.py <file.dae> <out.gltf dir> [--drop-driver]
import sys, os, re, json, struct, io
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
DROP_DRIVER = '--drop-driver' in sys.argv
os.makedirs(outdir, exist_ok=True)
NS = '{http://www.collada.org/2005/11/COLLADASchema}'
root = ET.parse(src).getroot()
srcdir = os.path.dirname(src)

def fa(e): return np.array(e.text.split(), dtype=np.float64) if e is not None and e.text else np.zeros(0)
def tag(t): return NS + t

images = {i.get('id'): i.find(tag('init_from')).text for i in root.iter(tag('image'))}
effects = {}
for ef in root.iter(tag('effect')):
    d = ef.find('.//' + tag('diffuse'))
    c = d.find(tag('color')); t = d.find(tag('texture'))
    img = None
    if t is not None:
        samp = t.get('texture')
        for np_ in ef.iter(tag('newparam')):
            if np_.get('sid') == samp:
                surf = np_.find('.//' + tag('source')).text
                for np2 in ef.iter(tag('newparam')):
                    if np2.get('sid') == surf: img = np2.find('.//' + tag('init_from')).text
    effects[ef.get('id')] = (list(map(float, c.text.split())) if c is not None else None, img)
materials = {m.get('id'): effects[m.find(tag('instance_effect')).get('url')[1:]] for m in root.iter(tag('material'))}

# colour by Mecabricks/LEGO id (linear), from the file where available
colour = {}
for mid, (c, img) in materials.items():
    m = re.match(r'MB\|(\d+)-material$', mid)
    if m and c: colour[m.group(1)] = c[:3]
colour.setdefault('316', [0.20, 0.20, 0.21])   # titanium metallic
PBR = {'26': (0.0, 0.45), '1': (0.0, 0.5), '21': (0.0, 0.45), '316': (0.85, 0.35), '40': (0.0, 0.08)}

geoms = {g.get('id'): g for g in root.iter(tag('geometry'))}
gcache = {}
def load_geom(gid):
    if gid in gcache: return gcache[gid]
    g = geoms[gid]; mesh = g.find(tag('mesh'))
    srcs = {}
    for s in mesh.findall(tag('source')):
        acc = s.find('.//' + tag('accessor'))
        srcs[s.get('id')] = fa(s.find(tag('float_array'))).reshape(-1, int(acc.get('stride')))
    vmap = {}
    for v in mesh.findall(tag('vertices')):
        for i in v.findall(tag('input')):
            if i.get('semantic') == 'POSITION': vmap[v.get('id')] = i.get('source')[1:]
    prims = []
    for tr in mesh.findall(tag('triangles')):
        ins = tr.findall(tag('input')); stride = max(int(i.get('offset')) for i in ins) + 1
        p = np.array(tr.find(tag('p')).text.split(), dtype=np.int64).reshape(-1, stride)
        d = {'mat': tr.get('material'), 'uv': {}}
        for i in ins:
            sem, sid, off = i.get('semantic'), i.get('source')[1:], int(i.get('offset'))
            if sem == 'VERTEX': d['pos'] = srcs[vmap[sid]][p[:, off]]
            elif sem == 'NORMAL': d['nrm'] = srcs[sid][p[:, off]]
            elif sem == 'TEXCOORD': d['uv'][i.get('set')] = srcs[sid][p[:, off]]
        prims.append(d)
    gcache[gid] = prims
    return prims

# minifig: hips/legs, arms, hands, torso, head, helmet
DRIVER_NODES = {'Part_%d' % i for i in (0, 1, 2, 3, 4, 5, 6, 7, 70, 212)}
groups = {}  # material -> lists
parts = 0
for node in root.iter(tag('node')):
    ig = node.find(tag('instance_geometry'))
    if ig is None: continue
    gid = ig.get('url')[1:]
    name = geoms[gid].get('name')
    if DROP_DRIVER and node.get('id') in DRIVER_NODES: continue
    parts += 1
    M = np.array(node.find(tag('matrix')).text.split(), dtype=np.float64).reshape(4, 4)
    binds = {}
    for im in ig.iter(tag('instance_material')):
        bv = im.find(tag('bind_vertex_input'))
        binds[im.get('symbol')] = (im.get('target')[1:], bv.get('input_set') if bv is not None else None)
    R = M[:3, :3]; N = np.linalg.inv(R).T; flip = np.linalg.det(R) < 0
    for pr in load_geom(gid):
        mat, uvset = binds.get(pr['mat']) or (list(binds.values())[0] if len(binds) == 1 else (pr['mat'], None))
        pos = pr['pos'] @ R.T + M[:3, 3]
        nrm = pr['nrm'] @ N.T; nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
        uv = pr['uv'].get(uvset) if uvset is not None else None
        if flip:
            o = np.arange(len(pos)).reshape(-1, 3)[:, ::-1].ravel()
            pos, nrm = pos[o], nrm[o]; uv = uv[o] if uv is not None else None
        groups.setdefault(mat, []).append((pos, nrm, uv, name))

print('parts', parts, 'materials', len(groups))

# build glTF
bin_ = bytearray(); views = []; accs = []; meshes = []; mats = []; texs = []; imgs = []; nodes = []
def add_view(b, target=None):
    while len(bin_) % 4: bin_.append(0)
    views.append({'buffer': 0, 'byteOffset': len(bin_), 'byteLength': len(b), **({'target': target} if target else {})})
    bin_.extend(b); return len(views) - 1
def add_acc(a, ctype, typ, target, minmax=False):
    v = add_view(a.tobytes(), target)
    acc = {'bufferView': v, 'componentType': ctype, 'count': len(a), 'type': typ}
    if minmax: acc['min'] = a.min(0).tolist(); acc['max'] = a.max(0).tolist()
    accs.append(acc); return len(accs) - 1

def lin2srgb(c): c = np.clip(c, 0, 1); return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

tot = 0
for mat, lst in sorted(groups.items()):
    pos = np.concatenate([l[0] for l in lst]) * 0.001  # mm -> m
    nrm = np.concatenate([l[1] for l in lst])
    has_uv = all(l[2] is not None for l in lst)
    uv = np.concatenate([l[2] for l in lst]) if has_uv else None
    # weld
    key = np.concatenate([np.round(pos * 1e5), np.round(nrm * 1e3)] + ([np.round(uv * 1e4)] if has_uv else []), axis=1)
    uq, inv = np.unique(key, axis=0, return_inverse=True)
    first = np.zeros(len(uq), dtype=np.int64); first[inv[::-1]] = np.arange(len(inv))[::-1]
    P = pos[first].astype(np.float32); Nn = nrm[first].astype(np.float32); idx = inv.astype(np.uint32).ravel()
    attrs = {'POSITION': add_acc(P, 5126, 'VEC3', 34962, True), 'NORMAL': add_acc(Nn, 5126, 'VEC3', 34962)}
    m = re.match(r'MB\|(\d+)(?:\|(\w+))?-material', mat); cid, deco = m.group(1), m.group(2)
    eff = materials[mat]
    base = colour.get(cid, [1, 0, 1])
    metal, rough = PBR.get(cid, (0.0, 0.5))
    md = {'name': f'c{cid}' + (f'-{deco}' if deco else ''), 'pbrMetallicRoughness': {'metallicFactor': metal, 'roughnessFactor': rough}}
    if deco and has_uv:
        T = uv.astype(np.float32)[first].copy(); T[:, 1] = 1 - T[:, 1]
        attrs['TEXCOORD_0'] = add_acc(T, 5126, 'VEC2', 34962)
        im = Image.open(os.path.join(srcdir, images[eff[1]])).convert('RGBA')
        bg = Image.new('RGBA', im.size, tuple(int(round(x * 255)) for x in lin2srgb(np.array(base))) + (255,))
        comp = Image.alpha_composite(bg, im).convert('RGB')
        if max(comp.size) > 512: comp = comp.resize((min(512, comp.size[0]), min(512, comp.size[1]) if comp.size[1] >= comp.size[0] else comp.size[1] * 512 // comp.size[0]), Image.LANCZOS)
        b = io.BytesIO(); comp.save(b, 'PNG', optimize=True)
        iv = add_view(bytes(b.getvalue()))
        imgs.append({'bufferView': iv, 'mimeType': 'image/png', 'name': deco}); texs.append({'source': len(imgs) - 1, 'sampler': 0})
        md['pbrMetallicRoughness']['baseColorTexture'] = {'index': len(texs) - 1}
    else:
        md['pbrMetallicRoughness']['baseColorFactor'] = base + [1.0]
    if cid == '40':
        md['pbrMetallicRoughness']['baseColorFactor'] = [0.9, 0.92, 0.95, 0.35]; md['alphaMode'] = 'BLEND'
    mats.append(md)
    ia = add_acc(idx, 5125, 'SCALAR', 34963)
    meshes.append({'name': md['name'], 'primitives': [{'attributes': attrs, 'indices': ia, 'material': len(mats) - 1}]})
    nodes.append({'mesh': len(meshes) - 1, 'name': md['name']})
    tot += len(idx) // 3
    print(f'{mat:28s} verts {len(P):7d} tris {len(idx)//3:7d}' + (' uv' if has_uv else ''))

gl = {'asset': {'version': '2.0', 'generator': 'dae2gltf (Mecabricks W15 by jwf1)'}, 'scene': 0,
      'scenes': [{'nodes': list(range(len(nodes)))}], 'nodes': nodes, 'meshes': meshes, 'materials': mats,
      'accessors': accs, 'bufferViews': views, 'buffers': [{'byteLength': len(bin_)}]}
if texs: gl.update(textures=texs, images=imgs, samplers=[{'magFilter': 9729, 'minFilter': 9987}])
js = json.dumps(gl, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
while len(bin_) % 4: bin_.append(0)
out = os.path.join(outdir, 'w15' + ('-nodriver' if DROP_DRIVER else '') + '.glb')
with open(out, 'wb') as f:
    f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(bin_)))
    f.write(struct.pack('<II', len(js), 0x4E4F534A)); f.write(js)
    f.write(struct.pack('<II', len(bin_), 0x004E4942)); f.write(bin_)
print('tris', tot, 'bytes', os.path.getsize(out), out)
