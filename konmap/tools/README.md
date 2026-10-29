# konmap/tools

Run from anywhere; paths resolve against `konmap/`. Python 3.

## New city (research report → city file)
1. `parse_report.py <report.md> <blocks.json>` — split a research report into site blocks (key, fields, coords, ratings).
2. Write `cities/<id>/curation.json` by hand: the stops kept (report key, kind, main/minor, checked pin, address) and the
   area routes. Field list at the top of `build_city.py`.
3. `build_city.py <id> <blocks.json> [...]` — writes `cities/<id>/city.json` (keeps existing tours and events).
4. `clip_land.py <raw> <id>` then `build_base.py <id> <raw>` — drawn base map `cities/<id>/base.json`.
5. Optional: `add_streets.py <id> <osm.geojson> "<attribution>"` — real street map.
6. Add the city to `cities/index.json` and `REGISTRY.md`, commit, republish KonMap.

## Old single-page map → city file
`migrate_page.py <id> <legacy index.html> <legacy base.json> ["<helpNote>"]` (template-kit pages: Rome, Athens, Plovdiv).

## Engine
- `loader.js` — the loader appended to every engine page (`__ENGINE_CFG__` = engine defaults).
- `make_engine_0.3.py` — how concrete/0.3 was made from Turin 2.2 + tours (one-off, record). The next engine version
  is a copy of the 0.3 folder, edited; no script needed.
