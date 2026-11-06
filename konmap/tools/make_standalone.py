"""One city as a single self-contained page (engine + city data + base map + reports + glyphs + Leaflet inlined), for sharing.
usage: make_standalone.py <id> <out.html> [lang]
lang (e.g. es): city text from cities/<id>/<lang>/city.json and reports.json (base map shared), engine interface text
translated with tools/i18n/<lang>.py. A fetch shim serves the inlined data; the Cities button is hidden.
Still online: fonts and the MapLibre street-map libraries (jsdelivr), as in KonMap."""
import json, sys, os, re, importlib.util
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cid, out = sys.argv[1], sys.argv[2]; lang = sys.argv[3] if len(sys.argv) > 3 else ''
cdir = f'{B}/cities/{cid}'; tdir = f'{cdir}/{lang}' if lang else cdir
city = json.load(open(f'{tdir}/city.json'))
eng = open(f'{B}/engines/{city["meta"]["engine"]}/index.html').read()
if lang:
    spec = importlib.util.spec_from_file_location('t', f'{B}/tools/i18n/{lang}.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    head, rest = eng.split('<body', 1); miss = []
    for en in sorted(m.T, key=len, reverse=True):
        es = m.T[en]; n0 = rest
        if ' ' in en.strip() or not en.strip().isalpha() or len(en) > 12:
            rest = rest.replace(en, es)
        else:
            for q in ("'%s'", '"%s"', '>%s<'):
                rest = rest.replace(q % en, q % es)
        if rest == n0: miss.append(en)
    eng = head.replace('<html lang="en"', f'<html lang="{lang}"') + '<body' + rest
    if miss: print('not found:', miss)
files = {f'cities/{cid}/city.json': f'{tdir}/city.json', 'shared/glyphs.json': f'{B}/shared/glyphs.json'}
for k in ('baseFile', 'reportsFile'):
    f = city['cfg'].get(k)
    if f: files[f'cities/{cid}/{f}'] = f'{tdir}/{f}' if os.path.exists(f'{tdir}/{f}') else f'{cdir}/{f}'
data = {p: json.load(open(f)) for p, f in files.items()}
blob = json.dumps(data, separators=(',', ':'), ensure_ascii=False).replace('</', '<\\/')
shim = ('<script type="application/json" id="konmapData">' + blob + '</script>\n<script>\n'
        f'window.KONMAP_CITY={json.dumps(cid)};\n'
        '(function(){var D=JSON.parse(document.getElementById("konmapData").textContent),f=window.fetch;'
        'window.fetch=function(u){var k=String(u).replace(/^(\\.\\.\\/)+/,"").replace(/^\\.\\//,"");'
        'if(D[k]) return Promise.resolve(new Response(JSON.stringify(D[k]),{status:200,headers:{"Content-Type":"application/json"}}));'
        'return f.apply(this,arguments);};})();\n</script>\n'
        '<style>#citiesBtn{display:none!important}</style>\n')
tag = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>'
lf = open(f'{B}/shared/vendor/leaflet-1.9.4.js').read().replace('</script', '<\\/script')
assert tag in eng
eng = eng.replace(tag, shim + '<script>' + lf + '</script>')
open(out, 'w').write(eng)
print(out, os.path.getsize(out))
