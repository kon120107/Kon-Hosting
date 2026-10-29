"""Add a real street layer to a city's base map from an OpenStreetMap extract (GeoJSON of highways + railways).
usage: add_streets.py <id> <osm.geojson> "<attribution line>"
Writes `streets` (n name, c class) and OSM `rails_far` into cities/<id>/base.json, and drops the generalised Natural
Earth roads where real streets exist. The engine then draws the street map (and street names, via shared/glyphs.json).
Getting an extract: the sandbox reaches only GitHub/npm/PyPI, so either a GitHub-hosted extract, or Kon downloads one
and attaches it (Turin, 28 Oct 2026: Kaggle "Turin street paths dataset", turin.geojson, 2020 Overpass export).
Needs: pip install shapely
"""
import json, sys, os, collections
from shapely.geometry import shape, LineString, MultiPoint
from shapely.ops import linemerge
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid, src, attr = sys.argv[1], sys.argv[2], sys.argv[3]
P = f'{B}/cities/{cid}/base.json'; Q = 1e5
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
    gs = [g] if g.geom_type == 'LineString' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'LineString']
    rs = [r for r in (qring(l.coords) for l in gs) if len(r) >= 4]
    return rs or None
CLS = {'motorway': 'mw', 'motorway_link': 'mw', 'trunk': 'mw', 'trunk_link': 'mw', 'primary': 'pri', 'primary_link': 'pri',
       'secondary': 'sec', 'secondary_link': 'sec', 'tertiary': 'ter', 'tertiary_link': 'ter', 'residential': 'res',
       'unclassified': 'res', 'living_street': 'res', 'road': 'res', 'service': 'svc', 'pedestrian': 'ped', 'path': 'ped', 'track': 'ped'}
d = json.load(open(src)); groups = collections.defaultdict(list); rails = []
for f in d['features']:
    p = f['properties']; g = shape(f['geometry'])
    if p.get('railway') == 'rail' and g.geom_type == 'LineString': rails.append(g); continue
    c = CLS.get(p.get('highway'))
    if not c: continue
    if g.geom_type == 'Polygon': g = g.exterior
    if g.geom_type == 'LineString': groups[(p.get('name') or '', c)].append(g)
sf = []; pts = []
for (n, c), gs in groups.items():
    e = enc_line((linemerge(gs) if len(gs) > 1 else gs[0]).simplify(0.000008))
    if e: sf.append([n, c, e])
    pts += [pt for l in gs for pt in l.coords[::20]]
cover = MultiPoint(pts).convex_hull.buffer(0.002)
base = json.load(open(P))
base['layers']['streets'] = {'t': 'line', 'p': ['n', 'c'], 'f': sf}
if rails: base['layers']['rails_far'] = {'t': 'line', 'p': [], 'f': [[e] for e in (enc_line(g.simplify(0.00001)) for g in rails) if e]}
def dec(a):
    x = y = 0; out = []
    for i in range(0, len(a), 2): x += a[i]; y += a[i + 1]; out.append((x / Q, y / Q))
    return out
kept = []
for f in base['layers'].get('roads_far', {}).get('f', []):
    for ring in f[-1]:
        o = LineString(dec(ring)).difference(cover)
        e = None if o.is_empty else enc_line(o)
        if e: kept.append([f[0], e])
if 'roads_far' in base['layers']: base['layers']['roads_far']['f'] = kept
base['attr'] = attr
json.dump(base, open(P, 'w'), separators=(',', ':'), ensure_ascii=False)
print(cid, len(sf), 'street features;', len(rails), 'rail lines')
