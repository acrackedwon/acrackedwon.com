import json, math
S=[]
def both(id, logo, y, z, w, xo=60, n=None, up=None, **kw):
    for sx in (1,-1):
        s=dict(id=f'{id}{"R" if sx>0 else "L"}', logo=logo, o=[sx*xo,y,z], d=[-sx,0,0], w=w, **kw)
        if n: s['n']=[sx*n[0],n[1],n[2]]
        if up: s['up']=[sx*up[0],up[1],up[2]]
        S.append(s)
# rear wing: PETRONAS + teal tips, Snapdragon endplates
S.append(dict(id='rw-petronas', logo='petronas', o=[0,80,89.5], d=[0,-1,0], up=[0,0,1], w=34, depth=3))
for sx in (1,-1): S.append(dict(id=f'rw-teal{sx}', logo='tealbar', o=[sx*21.3,80,89.5], d=[0,-1,0], up=[0,0,1], w=3.6, h=5.2, depth=3))
both('rw-snap', 'snapdragon', 29.5, 88, 11)
# airbox: white INEOS (red-rimmed intake comes from the repaint)
both('ab-ineos', 'ineosBold', 33.5, 15.4, 11.5, xo=40, n=[0.94,0.34,0], depth=6)
# engine cover shoulder: TeamViewer; cockpit side: AMD; floor: E PERFORMANCE
both('ec-tv', 'teamviewer', 28.4, 44.5, 14.5, up=[0,1,0], minDot=0.3)
both('ck-amd', 'amd', 26.1, 1.8, 5.5)
both('fl-ep', 'eperf', 5.6, 40, 11)
# halo: CROWDSTRIKE along the side bars
for sx in (1,-1): S.append(dict(id=f'halo-cs{sx}', logo='crowdstrike', o=[sx*12.5,80,-3], d=[0,-1,0], up=[-sx,0,0], w=8, depth=3, minDot=0.3))
# front wing: white INEOS on endplates, PETRONAS on the top plane
both('fw-ineos', 'ineosBold', 7.5, -82, 9.5)
for sx in (1,-1): S.append(dict(id=f'fw-pet{sx}', logo='petronas', o=[sx*15,60,-97], d=[0,-1,0], n=[0,1,0], up=[0,0,1], w=7.5, depth=4))
# nose: star at the tip, PETRONAS emblem on top, teal line + AMG along the sides
S.append(dict(id='n-star', logo='star', o=[0,60,-93], d=[0,-1,0], up=[0,0,1], w=5.6))
S.append(dict(id='n-emblem', logo='petronasEmblem', o=[0,60,-56], d=[0,-1,0], up=[0,0,1], w=3.4))
def slope(k): return [0, 1, -k]
both('n-lineA', 'stripe', 12.85, -89, 19, xo=12, up=slope(0.27), h=0.65, depth=2)
both('n-lineB', 'stripe', 17.35, -66, 30, xo=12, up=slope(0.12), h=0.65, depth=2)
both('n-amg', 'amg', 15.7, -67, 9, xo=12, up=slope(0.12))
json.dump(S,open('specs-w14.json','w'),indent=0)
print(len(S))
