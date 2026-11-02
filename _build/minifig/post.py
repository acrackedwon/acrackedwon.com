"""Site prep for a rigged minifig GLB (from minifig2glb.py): close the neck gap,
drop the baked clips (the site animates procedurally) and weld duplicate
vertices so each primitive is indexed. Rendering is unchanged; the file shrinks."""
import json, struct, sys
import numpy as np
src, dst = sys.argv[1], sys.argv[2]
b = open(src, 'rb').read()
n = struct.unpack('<I', b[12:16])[0]
j = json.loads(b[20:20 + n]); bin_ = b[20 + n + 8:]
for nd in j['nodes']:
    if nd.get('name') == 'Head':
        nd['translation'][1] = round(nd['translation'][1] - 0.0016, 6)   # 4 LDU down: no white band at the neck
j.pop('animations', None)
def arr(ai):
    a = j['accessors'][ai]; v = j['bufferViews'][a['bufferView']]
    x = np.frombuffer(bin_[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']],
                      dtype=np.float32 if a['componentType'] == 5126 else np.uint32 if a['componentType'] == 5125 else np.uint16)
    return x.reshape(-1, 3) if a['type'] == 'VEC3' else x
out, views, accs = bytearray(), [], []
def put(data, target):
    raw = data.tobytes(); views.append({'buffer': 0, 'byteOffset': len(out), 'byteLength': len(raw), 'target': target})
    out.extend(raw + b'\0' * (-len(raw) % 4)); return len(views) - 1
for m in j['meshes']:
    for p in m['primitives']:
        P, N = arr(p['attributes']['POSITION']), arr(p['attributes']['NORMAL'])
        I = arr(p['indices']) if 'indices' in p else np.arange(len(P))
        u, inv = np.unique(np.concatenate([P, N], 1)[I], axis=0, return_inverse=True)
        pos, nrm = np.ascontiguousarray(u[:, :3], np.float32), np.ascontiguousarray(u[:, 3:], np.float32)
        idx = inv.reshape(-1).astype(np.uint16 if len(u) < 65536 else np.uint32)
        accs.append({'bufferView': put(pos, 34962), 'componentType': 5126, 'count': len(pos), 'type': 'VEC3',
                     'min': pos.min(0).tolist(), 'max': pos.max(0).tolist()})
        accs.append({'bufferView': put(nrm, 34962), 'componentType': 5126, 'count': len(nrm), 'type': 'VEC3'})
        accs.append({'bufferView': put(idx, 34963), 'componentType': 5123 if idx.dtype == np.uint16 else 5125, 'count': len(idx), 'type': 'SCALAR'})
        p['attributes'] = {'POSITION': len(accs) - 3, 'NORMAL': len(accs) - 2}; p['indices'] = len(accs) - 1
j['accessors'], j['bufferViews'], j['buffers'] = accs, views, [{'byteLength': len(out)}]
js = json.dumps(j, separators=(',', ':')).encode(); js += b' ' * (-len(js) % 4)
with open(dst, 'wb') as f:
    f.write(struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(out)))
    f.write(struct.pack('<II', len(js), 0x4E4F534A) + js)
    f.write(struct.pack('<II', len(out), 0x004E4942) + bytes(out))
print(dst, 12 + 16 + len(js) + len(out), 'bytes')
