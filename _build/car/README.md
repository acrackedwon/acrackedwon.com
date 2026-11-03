# LEGO Speed Champions 77244 — Mercedes-AMG F1 W15

Model: "Mercedes-AMG PETRONAS F1 Team W15 E Performance" by **jwf1** on Mecabricks
(https://www.mecabricks.com/en/models/MgaXpqnzaz0), exported as Collada (.dae).
Driver removed; sponsor decals added after the 2024 race livery.

`w15.glb` (≈850 KB, 259 parts + one decal mesh, meshopt-compressed):

    python3 -I dae2gltf.py "<export>/….dae" out --drop-driver      # → out/w15-nodriver.glb
    npx gltfpack@0.24.0 -i out/w15-nodriver.glb -o out/w15-nd-s.glb -si 0.3 -slb -noq
    python3 specs.py                                                # → specs.json (decal list)
    CAR=out/w15-nd-s.glb node decal.cjs build specs.json shot --export out/w15-decal.glb
    npx gltfpack@0.24.0 -i out/w15-decal.glb -o w15.glb -cc

- `dae2gltf.py`: merges parts by material, takes each print's UV set from `bind_vertex_input`,
  bakes base colour + print PNG into opaque textures. Metres, Y up, nose toward −Z.
- `logos.js`: rasterises the brand marks (SVGs in `logos/`, lettering in Inter) into one atlas.
- `decal.html` / `decal.cjs`: Playwright + three.js r170; projects each logo onto the
  simplified car with DecalGeometry (raycast hit, size in mm), merges them into one
  `decals` mesh (alphaTest), exports GLB. Decals are projected *after* simplification so
  they sit on the final surfaces. Serve the folder over http; needs three r170 in `vendor/`
  (three.module.min.js, GLTFLoader, GLTFExporter, DecalGeometry, RoomEnvironment, BufferGeometryUtils).
- Livery reference: Mercedes W15, 2024 (PETRONAS rear wing / sidepods / front wing, INEOS airbox,
  rear wing and front endplates, Snapdragon rear endplates, TeamViewer cockpit and floor,
  SOLERA and star pattern on the engine cover, AMG and star on the nose).
- Trademarks belong to their owners; fan-made decoration only. The GLB uses EXT_meshopt_compression,
  so GLTFLoader needs `setMeshoptDecoder`.
