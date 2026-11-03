# LEGO Speed Champions 77244 — Mercedes-AMG F1 W15

Model: "Mercedes-AMG PETRONAS F1 Team W15 E Performance" by **jwf1** on Mecabricks
(https://www.mecabricks.com/en/models/MgaXpqnzaz0), exported as Collada (.dae).

`w15.glb` (651 KB, 269 parts, includes the driver):

    python3 -I dae2gltf.py "<export>/Mercedes-AMG PETRONAS F1 Team W15 E Performance.dae" out   # [--drop-driver]
    npx gltfpack@0.24.0 -i out/w15.glb -o w15.glb -cc -si 0.3 -slb

`dae2gltf.py` merges parts by material, takes each decal's UV set from `bind_vertex_input`,
and bakes base colour + decal PNG into opaque textures. Units: metres, Y up, nose toward -Z.
The output uses EXT_meshopt_compression, so GLTFLoader needs `setMeshoptDecoder`.
