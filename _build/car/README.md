# LEGO Speed Champions 77244 — Mercedes-AMG F1 W15

Model: "Mercedes-AMG PETRONAS F1 Team W15 E Performance" by **jwf1** on Mecabricks
(https://www.mecabricks.com/en/models/MgaXpqnzaz0), exported as Collada (.dae).
Driver removed; repainted and decorated after the **W14 (2023)** race livery.

`car.glb` (≈870 KB, 259 parts + one decal mesh, meshopt-compressed):

    python3 -I dae2gltf.py "<export>/….dae" out --drop-driver --paint paint-w14.json   # → out/w15-nodriver.glb
    npx gltfpack@0.24.0 -i out/w15-nodriver.glb -o out/w15-nd-s.glb -si 0.3 -slb -noq -kn
    python3 specs-w14.py                                            # → specs-w14.json (decal list)
    CAR=out/w15-nd-s.glb node decal.cjs build specs-w14.json shot --export out/w15-decal.glb
    npx gltfpack@0.24.0 -i out/w15-decal.glb -o car.glb -cc -kn

- `dae2gltf.py`: merges parts by material (the four wheel assemblies — tyre, hub cover, hub bits — go into
  their own nodes `wheel_FL/FR/RL/RR`, origin on the axle, so the site can spin them), takes each print's UV set from `bind_vertex_input`,
  bakes base colour + print PNG into opaque textures. Metres, Y up, nose toward −Z.
- `logos.js`: rasterises the brand marks (SVGs in `logos/`, lettering in Inter) into one atlas.
- `decal.html` / `decal.cjs`: Playwright + three.js r170; projects each logo onto the
  simplified car with DecalGeometry (raycast hit, size in mm), merges them into one
  `decals` mesh (alphaTest), exports GLB. Decals are projected *after* simplification so
  they sit on the final surfaces. Serve the folder over http; needs three r170 in `vendor/`
  (three.module.min.js, GLTFLoader, GLTFExporter, DecalGeometry, RoomEnvironment, BufferGeometryUtils).
- `paint-w14.json`: node id → colour id. The W15's silver nose, airbox and teal deck go black;
  the airbox intake goes red (W14's red-rimmed inlet).
- Livery reference: Mercedes W14, 2023 (Wikimedia Commons photos): PETRONAS + teal tips on the
  rear wing, Snapdragon endplates, white INEOS on the airbox and front endplates, TeamViewer on the
  engine-cover shoulder, AMD by the cockpit, CROWDSTRIKE on the halo, E PERFORMANCE on the floor,
  teal line + AMG along the nose, star at the tip, PETRONAS emblem on the nose and front wing.
- Trademarks belong to their owners; fan-made decoration only. The GLB uses EXT_meshopt_compression,
  so GLTFLoader needs `setMeshoptDecoder`.
