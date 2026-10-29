// ---------- loader (engine concrete 0.3) ----------
// Opened directly (engines/concrete/0.3/index.html#turin) or written in by the launcher (index.html#turin).
// The city comes from the #hash (artifact viewers pass only a plain #name). Data: cities/<id>/city.json.
(function(){
  var ENGINE='concrete/0.3', ECFG=__ENGINE_CFG__;
  var ROOT=/\/engines\/[^\/]+\/[^\/]+\/[^\/]*$/.test(location.pathname)?'../../../':'';
  var city=(location.hash||'').replace(/^#/,'')||new URLSearchParams(location.search).get('city');
  window.addEventListener('hashchange',function(){ location.reload(); });
  function fail(msg){ document.body.insertAdjacentHTML('afterbegin','<div style="padding:16px;font:14px system-ui">'+msg+' <a href="#" onclick="location.hash=\'\';location.reload();return false">All cities</a></div>'); }
  if(!city){ fail('No city chosen.'); return; }
  var dir=ROOT+'cities/'+encodeURIComponent(city)+'/';
  fetch(dir+'city.json').then(function(r){ if(!r.ok) throw new Error('city '+r.status); return r.json(); }).then(function(d){
    if(d.meta.engine!==ENGINE) console.warn('city asks for engine '+d.meta.engine+', running '+ENGINE);
    var cfg={}, k; for(k in ECFG) cfg[k]=ECFG[k]; for(k in d.cfg) cfg[k]=d.cfg[k];
    if(cfg.baseFile) cfg.baseFile=dir+cfg.baseFile;
    if(cfg.reportsFile) cfg.reportsFile=dir+cfg.reportsFile;
    cfg.glyphFile=ROOT+'shared/glyphs.json';
    var cc=d.cc; cc.tours=d.tours||[];
    document.title=d.meta.name+' · KonMap';
    var n=document.getElementById('cityName'); if(n) n.textContent=d.meta.name+' Concrete Map';
    var h=document.getElementById('cityNote'); if(h) h.textContent=cc.helpNote||'';
    KONMAP_ENGINE(cfg,cc,d.data,d.guide,d.offids,d.evdata,d.routes,d.paths);
  }).catch(function(e){ console.error(e); fail('Could not load city “'+city+'”: '+e.message+'.'); });
})();
