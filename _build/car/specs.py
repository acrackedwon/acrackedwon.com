import json
S=[]
def both(id, logo, y, z, w, xo=60, n=None, **kw):
    for sx in (1,-1):
        s=dict(id=f'{id}{"R" if sx>0 else "L"}', logo=logo, o=[sx*xo,y,z], d=[-sx,0,0], w=w, **kw)
        if n: s['n']=[sx*n[0],n[1],n[2]]
        S.append(s)
# rear wing
S.append(dict(id='rw-petronas', logo='petronas', o=[0,80,89.5], d=[0,-1,0], up=[0,0,1], w=37, depth=3))
both('rw-snap', 'snapdragon', 29.5, 88, 11)
S.append(dict(id='rw-ineos', logo='ineos', o=[0,30.5,150], d=[0,0,-1], w=15))
# airbox, engine cover, cockpit, floor
both('ab-ineos', 'ineos', 33, 15.2, 10.5, xo=40, n=[0.94,0.34,0], depth=6)
both('ec-solera', 'solera', 24.6, 40, 8.5)
for i,(y,z,w) in enumerate([(30,35,3.2),(28.2,42,2.6),(30.2,45.5,2.2),(27.4,50,2.0)]):
    both(f'ec-star{i}', 'starBare', y, z, w, up=[0,1,0.4])
both('ck-tv', 'teamviewer', 26.1, 1.8, 10)
both('fl-tv', 'teamviewer', 5.6, 40, 11)
# front wing endplates
both('fw-ineos', 'ineos', 7.5, -82, 10)
# front wing top
for sx in (1,-1):
    S.append(dict(id=f'fw-pet{sx}', logo='petronas', o=[sx*15,60,-97], d=[0,-1,0], n=[0,1,0], up=[0,0,1], w=7.5, depth=4))
# nose
S.append(dict(id='n-star', logo='starDark', o=[0,60,-93], d=[0,-1,0], up=[0,0,1], w=5.6))
S.append(dict(id='n-emblem', logo='petronasEmblem', o=[0,60,-52], d=[0,-1,0], up=[0,0,1], w=3.4))
both('n-amg', 'amgDark', 12.6, -79, 9, xo=30)
json.dump(S,open('specs.json','w'),indent=0)
print(len(S))
