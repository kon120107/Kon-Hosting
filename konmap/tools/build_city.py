"""Build cities/<id>/city.json (engine concrete) from a hand-written curation file plus parsed report blocks.
usage: build_city.py <id> <blocks.json> [<blocks2.json> ...]
Input:  cities/<id>/curation.json  (written by hand, kept in Git; fields below)
Output: cities/<id>/city.json      (overwritten; tours and evdata in an existing city.json are kept)

curation.json: id, name, lat, bbox [w,s,e,n], core/center [[s,w],[n,e]], labels [[lat,lon,text,class]],
majorRivers, attr, baseOn, helpNote, lists [[key,label]], extrasNote, engine (default concrete/0.3),
sites[]: id (stable, never reused), key (report site key, e.g. A3), k (kind), main (1/0), ll [lat,lon] (checked pin;
else the report's coords), q (address), optional name/blurb/when overrides, nv (not verified), off (day trip), days.
routes[]: id, name, color, days, dset, when, summary, stops (ids in walking order; 'id+' = optional add-on).
Several reports: pass several blocks files; a key is looked up in the first file that has it, so prefix keys
per report in curation.json if they clash (e.g. 'b1:A3').
"""
import json, re, sys, math, os, datetime
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid = sys.argv[1]
C = json.load(open(f'{B}/cities/{cid}/curation.json'))
blocks = {}
for i, p in enumerate(sys.argv[2:]):
    for b in json.load(open(p)):
        blocks.setdefault(b['key'], b); blocks.setdefault(f"{os.path.basename(p).split('.')[0]}:{b['key']}", b)

def clean(t):
    return re.sub(r'\*\*|__', '', t or '').replace('⚠️', '').replace('  ', ' ').strip()
def sentences(t, n):
    t = clean(t)
    if len(t) <= n: return t
    out = ''
    for p in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“(])', t):
        if len(out) + len(p) + 1 > n and out: break
        out = (out + ' ' + p).strip()
    return out[:n].rsplit(' ', 1)[0] + '…' if len(out) > n + 40 else out
def nice_name(t):
    t = clean(t).split(' — ')[0]
    m = re.match(r'^(.{6,}?)\s*\(([^)]*)\)\s*$', t)
    if m and re.search(r'\d|&|day trip|strong|about', m.group(2)): t = m.group(1)
    return t.strip(' :')
def field(b, *names):
    for n in names:
        for k, v in (b or {}).get('f', {}).items():
            if k.lower().startswith(n.lower()): return v
    return ''
def ratings(b):
    t = (b or {}).get('raw', '') + ' ' + json.dumps((b or {}).get('f', {}), ensure_ascii=False)
    m = re.search(r'Interest\s*(\d)\D{1,6}Presence\s*(\d)', t) or re.search(r'\bI(\d)\s*/\s*P(\d)', t)
    return [int(m.group(1)), int(m.group(2))] if m else None

sights, offmap, offids, guide = [], [], [], {}
for s in C['sites']:
    b = blocks.get(s['key'])
    ll = s.get('ll') or (b or {}).get('ll'); assert ll, ('no coordinates', s['id'])
    name = s.get('name') or nice_name(b['title'])
    see = field(b, 'What you see', 'What / where', 'text')
    hist = ' '.join(x for x in [field(b, 'History'), field(b, 'Why it matters'), field(b, 'Link')] if x)
    stat = field(b, 'Status')
    blurb = s.get('blurb') or sentences(see or hist, 230)
    when = s.get('when') or sentences(stat, 260)
    nv = bool(s.get('nv'))
    paras = [p for p in [clean(see), clean(hist), clean(stat) if clean(stat) != when else ''] if p] if b else [blurb, when]
    guide[s['id']] = {'t': name, 'l': 'main stop' if s.get('main') else 'minor stop', 'p': paras,
                      's': f"Research ({s['key']}); pin {'checked against Google Places' if s.get('ll') else 'from the report, approximate'}."}
    rec = {'id': s['id'], 'name': name, 'lat': round(ll[0], 5), 'lon': round(ll[1], 5), 'main': bool(s.get('main')), 'opt': False,
           'blurb': blurb, 'when': when, 'nv': nv, 'q': s['q'], 'days': s.get('days'), 'k': s['k'], 'v': s['key'].split(':')[-1][0], 'ip': ratings(b)}
    if s.get('off'): offmap.append({k: rec[k] for k in ['name', 'blurb', 'when', 'q']}); offids.append(s['id'])
    else: sights.append(rec)

S = {x['id']: x for x in sights}
def km(a, b):
    la = math.radians((a['lat'] + b['lat']) / 2)
    return math.hypot((a['lat'] - b['lat']) * 111.2, (a['lon'] - b['lon']) * 111.32 * math.cos(la))
def plen(p): return sum(km(p[i], p[i + 1]) for i in range(len(p) - 1))
def improve(p):
    p = p[:]; better = True
    while better:
        better = False
        for i in range(1, len(p) - 1):
            for j in range(i + 1, len(p)):
                q = p[:i] + p[i:j + 1][::-1] + p[j + 1:]
                if plen(q) < plen(p) - 1e-9: p = q; better = True
    return p
routes = []
for r in C.get('routes', []):
    core = [S[x] for x in r['stops'] if not x.endswith('+')]
    best = improve(core)
    if plen(best) < plen(core) * 0.95: print(f"  route {r['id']}: reordered {plen(core):.2f} -> {plen(best):.2f} km"); core = best
    stops = [x['id'] for x in core]
    for o in [x[:-1] for x in r['stops'] if x.endswith('+')]:
        i = min(range(len(core)), key=lambda k: km(core[k], S[o])); stops.insert(stops.index(core[i]['id']) + 1, o + '+')
    routes.append({k: r[k] for k in ['id', 'name', 'color', 'days', 'dset', 'when', 'summary']} | {'stops': stops})

out_p = f'{B}/cities/{cid}/city.json'
old = json.load(open(out_p)) if os.path.exists(out_p) else {}
cc = {k: C[k] for k in ['lat', 'core', 'center', 'labels', 'attr', 'baseOn', 'lists', 'extrasNote', 'helpNote'] if k in C}
cc |= {'slug': cid, 'name': C['name']}
city = {'meta': {'id': cid, 'name': C['name'], 'engine': C.get('engine', 'concrete/0.3'), 'source': 'kon', 'updated': datetime.date.today().isoformat()},
        'cfg': old.get('cfg') or {'baseFile': 'base.json'}, 'cc': cc,
        'data': {'routes': [], 'sights': sights, 'offmap': offmap}, 'guide': guide, 'offids': offids,
        'evdata': old.get('evdata') or {'EV': [], 'CLOSED': [], 'LATER': [], 'start': None, 'note': ''},
        'routes': routes, 'paths': None, 'tours': old.get('tours') or []}
json.dump(city, open(out_p, 'w'), ensure_ascii=False, separators=(',', ':'))
onroute = {x.rstrip('+') for r in routes for x in r['stops']}
print(cid, len(sights), 'stops,', len(offmap), 'day trips,', len(routes), 'routes; not on a route:', [x['id'] for x in sights if x['id'] not in onroute])
