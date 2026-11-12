"""OSM .pbf (e.g. a BBBike extract: extract.bbbike.org, format 'Protocol Buffer (PBF)', box drawn round the city)
-> streets GeoJSON for add_streets.py + rivers.json (non-buried waterways).
Edit PBF and CEN (box with every street; outside it only tertiary and up) below. Needs: pip install osmium.
Athens, 12 Nov 2026: BBBike box 23.38-24.16 E, 37.62-38.21 N, 47 MB; Kon downloaded it on his computer in minutes.
Overpass was busy or blocked (406) that day; BBBike is now the first choice."""
import osmium, json
PBF='/mnt/user-data/uploads/planet_23_380_37_620_24_160_38_210_osm.pbf'
CEN=(23.60,37.920,23.82,38.035)  # all streets
MAJ={'motorway','motorway_link','trunk','trunk_link','primary','primary_link','secondary','secondary_link','tertiary','tertiary_link'}
feats=[];rivers=[]
class H(osmium.SimpleHandler):
    def way(self,w):
        t=w.tags
        hw=t.get('highway'); rw=t.get('railway'); ww=t.get('waterway')
        if not (hw or rw=='rail' or ww in ('river','stream','canal')): return
        try: cs=[(n.lon,n.lat) for n in w.nodes]
        except osmium.InvalidLocationError: return
        if len(cs)<2: return
        if hw:
            if hw not in MAJ:
                xs=[c[0] for c in cs];ys=[c[1] for c in cs]
                if not (CEN[0]<=min(xs) and max(xs)<=CEN[2] and CEN[1]<=min(ys) and max(ys)<=CEN[3]): return
            feats.append({'type':'Feature','properties':{'highway':hw,'name':t.get('name:en') and t.get('name') or t.get('name')},'geometry':{'type':'LineString','coordinates':cs}})
        elif rw=='rail':
            feats.append({'type':'Feature','properties':{'railway':'rail'},'geometry':{'type':'LineString','coordinates':cs}})
        else:
            (None if t.get('tunnel') or t.get('location')=='underground' else rivers.append((t.get('name') or '', ww, cs)))
H().apply_file(PBF,locations=True)
json.dump({'type':'FeatureCollection','features':feats},open('athens-streets.geojson','w'))
json.dump(rivers,open('rivers.json','w'))
print(len(feats),'features',len(rivers),'waterways')
