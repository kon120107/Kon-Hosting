"""One city as a single self-contained page (engine + city data + base map + reports + glyphs inlined), for sharing.
usage: make_standalone.py <id> <out.html>
The page needs no other files: a fetch shim serves the inlined data at the paths the engine asks for; Cities button hidden.
Only Leaflet still comes from cdnjs (as in KonMap)."""
import json, sys, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid, out = sys.argv[1], sys.argv[2]
city = json.load(open(f'{B}/cities/{cid}/city.json'))
eng = open(f'{B}/engines/{city["meta"]["engine"]}/index.html').read()
files = {f'cities/{cid}/city.json': f'{B}/cities/{cid}/city.json', 'shared/glyphs.json': f'{B}/shared/glyphs.json'}
for k in ('baseFile', 'reportsFile'):
    if city['cfg'].get(k): files[f'cities/{cid}/{city["cfg"][k]}'] = f'{B}/cities/{cid}/{city["cfg"][k]}'
data = {p: json.load(open(f)) for p, f in files.items()}
blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
shim = ('<script type="application/json" id="konmapData">' + blob + '</script>\n<script>\n'
        f'window.KONMAP_CITY={json.dumps(cid)};\n'
        '(function(){var D=JSON.parse(document.getElementById("konmapData").textContent),f=window.fetch;'
        'window.fetch=function(u){var k=String(u).replace(/^(\\.\\.\\/)+/,"").replace(/^\\.\\//,"");'
        'if(D[k]) return Promise.resolve(new Response(JSON.stringify(D[k]),{status:200,headers:{"Content-Type":"application/json"}}));'
        'return f.apply(this,arguments);};})();\n</script>\n'
        '<style>#citiesBtn{display:none!important}</style>\n')
i = eng.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet')
open(out, 'w').write(eng[:i] + shim + eng[i:])
print(out, os.path.getsize(out))
