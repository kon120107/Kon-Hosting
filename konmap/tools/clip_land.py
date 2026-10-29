"""Cut the global 10 m land file down to city boxes once (the file is one world polygon; clipping it inside
build_base takes forever). Writes <raw>/geomaps/<id>-land.geojson.
usage: clip_land.py <raw dir> <id> [<id> ...]   (bbox from cities/<id>/curation.json; input <raw>/geomaps/lands10m.geojson
from npm @geo-maps/earth-lands-10m, file map.geo.json)"""
import json, sys, os, shapely
from shapely.geometry import mapping
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw = sys.argv[1]
cities = {c: json.load(open(f'{B}/cities/{c}/curation.json'))['bbox'] for c in sys.argv[2:]}
G = json.load(open(raw + '/geomaps/lands10m.geojson'))
geoms = [f['geometry'] for f in G['features']] if 'features' in G else G['geometries']
acc = {c: [] for c in cities}
for g in geoms:
    for poly in (g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]):
        ring = poly[0]; x0 = min(p[0] for p in ring); x1 = max(p[0] for p in ring); y0 = min(p[1] for p in ring); y1 = max(p[1] for p in ring)
        for c, (W, S, E, N) in cities.items():
            if x1 < W or x0 > E or y1 < S or y0 > N: continue
            cl = shapely.clip_by_rect(shapely.geometry.Polygon(poly[0], poly[1:]), W - .01, S - .01, E + .01, N + .01)
            if not cl.is_empty: acc[c].append(cl.buffer(0))
for c in cities:
    json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {}, 'geometry': mapping(g)} for g in acc[c]]},
              open(f'{raw}/geomaps/{c}-land.geojson', 'w'))
    print(c, len(acc[c]), 'pieces')
