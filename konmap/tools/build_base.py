"""Build a city's drawn base map, cities/<id>/base.json, from open data on disk.
usage: build_base.py <id> <raw dir>          (reads cities/<id>/curation.json for bbox, majorRivers, attr)
Raw data, all reachable from the cloud sandbox (GitHub + npm), download once into <raw>:
- <raw>/ne/*.geojson  Natural Earth 10m (raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/):
  ne_10m_rivers_lake_centerlines, ne_10m_rivers_europe, ne_10m_lakes, ne_10m_lakes_europe, ne_10m_roads,
  ne_10m_railroads, ne_10m_urban_areas
- <raw>/geomaps/<id>-land.geojson  cut by clip_land.py from npm @geo-maps/earth-lands-10m (OSM coastlines, ODbL)
Layers: land, urban, water, rivers (n, w), roads_far (c: 2/1/0), rails_far. Streets: add_streets.py afterwards.
Needs: pip install geopandas shapely
"""
import json, sys, os
import geopandas as gpd
from shapely.geometry import box
from shapely.ops import unary_union
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid, RAW = sys.argv[1], sys.argv[2]
C = json.load(open(f'{B}/cities/{cid}/curation.json'))
OUT = f'{B}/cities/{cid}/base.json'
W, S, E, N = C['bbox']; BB = box(W, S, E, N); Q = 1e5
def qring(coords):
    out = []; px = py = 0; first = True; last = None
    for x, y in coords:
        ix, iy = round(x * Q), round(y * Q)
        if last == (ix, iy): continue
        last = (ix, iy)
        if first: out += [ix, iy]; first = False
        else: out += [ix - px, iy - py]
        px, py = ix, iy
    return out
def enc_line(g):
    if g.is_empty: return None
    gs = []
    for p in ([g] if g.geom_type == 'LineString' else getattr(g, 'geoms', [])):
        gs += [p] if p.geom_type == 'LineString' else list(p.geoms) if p.geom_type == 'MultiLineString' else []
    rs = [r for r in (qring(l.coords) for l in gs) if len(r) >= 4]
    return rs or None
def enc_poly(g):
    if g.is_empty: return None
    out = []
    for p in ([g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']):
        rings = [r for r in [qring(p.exterior.coords)] + [qring(i.coords) for i in p.interiors] if len(r) >= 8]
        if rings: out.append(rings)
    return out or None
def read(name):
    p = os.path.join(RAW, name)
    return gpd.read_file(p, bbox=(W, S, E, N)) if os.path.exists(p) else None
layers = {}
def add(name, t, props, feats): layers[name] = {'t': t, 'p': props, 'f': feats}; print(' ', name, len(feats))
tol = C.get('simplify', 0.00015)
L = read(f'geomaps/{cid}-land.geojson')
land = unary_union([g.buffer(0) for g in L.geometry]).intersection(BB).simplify(tol)
add('land', 'poly', [], [[e] for e in [enc_poly(land)] if e])
def polys(*names):
    out = []
    for n in names:
        G = read(n)
        if G is None: continue
        for g in G.geometry:
            e = enc_poly(g.buffer(0).intersection(BB).simplify(tol))
            if e: out.append([e])
    return out
add('urban', 'poly', [], polys('ne/ne_10m_urban_areas.geojson'))
add('water', 'poly', [], polys('ne/ne_10m_lakes.geojson', 'ne/ne_10m_lakes_europe.geojson'))
MAJOR = set(C.get('majorRivers', [])); rf = []
for n in ['ne/ne_10m_rivers_lake_centerlines.geojson', 'ne/ne_10m_rivers_europe.geojson']:
    G = read(n)
    if G is None: continue
    for _, r in G.iterrows():
        nm = str(r.get('name') or r.get('name_en') or ''); sr = r.get('scalerank', 9) or 9
        e = enc_line(r.geometry.intersection(BB).simplify(tol))
        if e: rf.append([nm, 2 if (nm in MAJOR or sr <= 5) else 1, e])
add('rivers', 'line', ['n', 'w'], rf)
R = read('ne/ne_10m_roads.geojson'); CL = {'Major Highway': 2, 'Secondary Highway': 1}; rd = []
if R is not None:
    for _, r in R.iterrows():
        e = enc_line(r.geometry.intersection(BB).simplify(tol))
        if e: rd.append([CL.get(r.get('type'), 0), e])
add('roads_far', 'line', ['c'], rd)
RL = read('ne/ne_10m_railroads.geojson'); rl = []
if RL is not None:
    for g in RL.geometry:
        e = enc_line(g.intersection(BB).simplify(tol))
        if e: rl.append([e])
add('rails_far', 'line', [], rl)
raw = json.dumps({'v': 1, 'bbox': C['bbox'], 'attr': C['attr'], 'layers': layers}, separators=(',', ':'), ensure_ascii=False)
open(OUT, 'w').write(raw); print(OUT, len(raw), 'bytes')
