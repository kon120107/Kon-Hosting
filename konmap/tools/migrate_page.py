"""Turn a legacy single-page city map (template kit 0.2 page, e.g. Rome/Athens/Plovdiv 1.0) into cities/<id>/.
usage: migrate_page.py <id> <legacy index.html> <legacy base.json> ["<helpNote>"]
The legacy page carries its data in lines `var CFG=… var CC=… var DATA=… var GUIDE=… var OFFIDS=… var EVDATA=…
var NR=… var PATHS=…`; read the page with the artifact tools (read_file) and its <slug>-base.json supporting file.
Copenhagen 1.2 (older Copenhagen engine) has no CC line: write its cc by hand (see docs/schema in the project).
Afterwards add the city to cities/index.json and REGISTRY.md.
"""
import json, os, sys, shutil, datetime
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid, page, base = sys.argv[1:4]; help_note = sys.argv[4] if len(sys.argv) > 4 else ''
V = {}
for l in open(page).read().split('\n'):
    for k in ['CFG', 'CC', 'DATA', 'GUIDE', 'OFFIDS', 'EVDATA', 'NR', 'PATHS']:
        if l.startswith('var ' + k + '='): V[k] = json.loads(l[len(k) + 5:].rstrip().rstrip(';'))
missing = [k for k in ['CC', 'DATA', 'GUIDE', 'NR'] if k not in V]; assert not missing, ('not found in page', missing)
cc = V['CC']; cc['helpNote'] = help_note or cc.get('baseOn', '')
cfg = {k: v for k, v in (V.get('CFG') or {}).items() if k in ('reports', 'metro')}; cfg['baseFile'] = 'base.json'
city = {'meta': {'id': cid, 'name': cc.get('name', cid.title()), 'engine': 'concrete/0.3', 'source': 'kon', 'updated': datetime.date.today().isoformat()},
        'cfg': cfg, 'cc': cc, 'data': V['DATA'], 'guide': V['GUIDE'], 'offids': V.get('OFFIDS', []),
        'evdata': V.get('EVDATA') or {'EV': [], 'CLOSED': [], 'LATER': [], 'start': None, 'note': ''},
        'routes': V['NR'], 'paths': None, 'tours': cc.pop('tours', [])}
d = f'{B}/cities/{cid}'; os.makedirs(d, exist_ok=True)
json.dump(city, open(d + '/city.json', 'w'), ensure_ascii=False, separators=(',', ':'))
shutil.copy(base, d + '/base.json')
print(cid, len(city['data']['sights']), 'stops,', len(city['routes']), 'routes ->', d)
