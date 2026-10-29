# One-off migration: Turin 2.2 single-page map -> concrete engine 0.3 + turin city data
import json,re,os,shutil,sys
src22, src20A, out = sys.argv[1], sys.argv[2], sys.argv[3]
H=open(src22+'/index.html').read().split('\n')
A=open(src20A+'/index.html').read().split('\n')
def var(lines,name):
    for l in lines:
        if l.startswith('var '+name+'='): return json.loads(l[len(name)+5:].rstrip().rstrip(';'))
V={k:var(H,k) for k in ['CFG','CC','DATA','GUIDE','OFFIDS','EVDATA','NR','PATHS']}
tours=var(A,'CC')['tours']
# ---- city data
cfg=V['CFG']
city_cfg={k:cfg[k] for k in ['reports','metro'] if k in cfg}
city_cfg['baseFile']='base.json'; city_cfg['reportsFile']='reports.json'
eng_cfg={k:cfg[k] for k in cfg if k not in ('reports','metro','baseFile','reportsFile')}
cc=V['CC']
cc['helpNote']="Base map: OpenStreetMap streets and rail (2020 extract, Turin city only; no buildings or parks yet). Outside that, Natural Earth rivers and main roads, generalised (can sit up to about 1 km off). Pins: checked against Google Places on 21 and 28 Oct 2026 where marked; others from the research report and approximate."
city={"meta":{"id":"turin","name":"Turin","engine":"concrete/0.3","source":"kon","updated":"2026-10-29",
       "history":"Turin Concrete Map 1.0 → 2.2 were separate artifacts; 2.2 plus the curated tours from 2.0A became this file."},
      "cfg":city_cfg,"cc":cc,"data":V['DATA'],"guide":V['GUIDE'],"offids":V['OFFIDS'],"evdata":V['EVDATA'],
      "routes":V['NR'],"paths":V['PATHS'],"tours":tours}
cd=out+'/cities/turin'; os.makedirs(cd,exist_ok=True)
json.dump(city,open(cd+'/city.json','w'),ensure_ascii=False,separators=(',',':'))
shutil.copy(src22+'/turin-base.json',cd+'/base.json'); shutil.copy(src22+'/turin-reports.json',cd+'/reports.json')
os.makedirs(out+'/shared',exist_ok=True); shutil.copy(src22+'/glyphs.json',out+'/shared/glyphs.json')
json.dump({"cities":[{"id":"turin","name":"Turin","engine":"concrete/0.3"}]},open(out+'/cities/index.json','w'),ensure_ascii=False,indent=1)
# ---- engine
txt='\n'.join(H)
# tours CSS (20A lines 2-13) after metro css
css='\n'.join(A[1:13])
txt=txt.replace('\n</style>', '\n'+css+'\n</style>',1)
# tours JS (20A module tours up to module scale) before boot
a0=A.index('// ---- module tours ----'); a1=next(i for i,l in enumerate(A) if l.startswith('// ---- module scale'))
tjs='\n'.join(A[a0:a1])
txt=txt.replace('\n// ---------- boot ----------','\n'+tjs+'\n// ---------- boot ----------',1)
# title / header / notes become city-driven
txt=txt.replace('<title>Turin Concrete Map 2.2</title>','<title>KonMap</title>')
txt=txt.replace('<h1>Turin Concrete Map <small>2.2</small></h1>','<h1><span id="cityName">KonMap</span> <small>engine 0.3</small></h1>')
txt=re.sub(r'<p class="vnote">.*?</p>','<p class="vnote"><b>Engine concrete 0.3</b> (29 Oct 2026): one engine for every city, loading the city from its data file; adds the curated tours (by era, by theme) first tried in Turin 2.0A. Built from Turin 2.2.</p>',txt,count=1,flags=re.S)
old_note=[l for l in H if l.strip().startswith('<p class="note">Base map: OpenStreetMap')][0]
txt=txt.replace(old_note,'    <p class="note" id="cityNote"></p>\n    <p class="note">Live location works only where the page may ask for it (the GitHub-hosted copy, not inside Claude).</p>',1)
# data vars -> function parameters
start=txt.index('<script>\n(function(){\nvar CFG=')
s2=txt.index('var PATHS=null;',start)+len('var PATHS=null;')
txt=txt[:start]+'<script>\nfunction KONMAP_ENGINE(CFG,CC,DATA,GUIDE,OFFIDS,EVDATA,NR,PATHS){'+txt[s2:]
end=txt.rindex('})();\n</script>')
loader=open(os.path.dirname(__file__)+'/loader.js').read().replace('__ENGINE_CFG__',json.dumps(eng_cfg))
txt=txt[:end]+'}\n'+loader+'\n</script>'+txt[end+len('})();\n</script>'):]
ed=out+'/engines/concrete/0.3'; os.makedirs(ed,exist_ok=True)
open(ed+'/index.html','w').write(txt)
print('ok', len(txt), 'tours', len(tours))
