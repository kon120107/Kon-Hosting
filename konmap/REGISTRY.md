# Registry

## Live artifacts — the ONLY ones Claude edits

| Artifact | Slug | Holds |
|---|---|---|
| KonMap | `4a7c9607-30c8-4227-9c02-8a2602db3250` | launcher, all engines, all migrated cities |
| KonMap Lab | not created yet | experiments; created on the first one |

Republish from this folder with `publish_files` (patch mode: send only the files that changed).

## Cities

| City | Engine | Status |
|---|---|---|
| Turin | concrete/0.3 | migrated 29 Oct 2026 (from Turin 2.2 + tours from 2.0A) |
| Plovdiv | concrete/0.3 | built from the research register 29 Oct 2026 (72 stops, 10 walks, 7 tours, 5 Study readings; drawn base, no streets) |
| Vatra Dornei | concrete/0.3 | built 30 Oct 2026 (34 stops); OSM street map 6 Nov 2026 |
| Cluj-Napoca | concrete/0.3 | short-stay map 5 Nov 2026: 24 stops, 1 half-afternoon walk, Study with 2 readings; OSM street map (2013 named-street extract, madeincluj/street-names), no river |
| Rome | concrete/0.3 | built from claude/rome/rome-sites.md 6 Nov 2026: 134 stops, 14 walks, 14 tours (church day as tours), 6 day trips, Study; drawn base with the Tevere, no streets |
| Copenhagen, Paris, Athens | — | legacy single-page artifacts; migrate one by one |

## Legacy artifacts (read-only, to be deleted when Kon says)

Turin Concrete Map 1.0, 1.0A, 2.0, 2.0A, 2.1, 2.2 · Copenhagen 1.1, 1.2 · Paris 4.1 · Rome 1.0 · Athens 1.0 ·
Plovdiv 1.0 (replaced by cities/plovdiv) · Apps (HTML holder prototype). Old GitHub Pages folders `turin-concrete-map/`, `paris-concrete-map/`.

## Change log

- 2026-10-29 — Restructure: engine `concrete/0.3` (from Turin 2.2's engine 0.2, now loads cities from data,
  adds the tours module from Turin 2.0A). Turin moved to `cities/turin/`. KonMap artifact created.
- 2026-10-29 — concrete/0.3 fixed in place: development notes removed from the panel (version line, engine note,
  technical notes under the Show slider, metro and walk maker); tours are no longer a Routes switch (By area / era /
  theme) but a collapsed "Tours by topic" box at the bottom of Routes, era tours grouped as "Periods of history";
  tour sort/filter box dropped; missing tours CSS (chips, notes, story box, day-trip box) restored; deck title for
  tours fixed. tools/: build_city, parse_report, build_base, clip_land, add_streets, migrate_page moved in from the
  old template kit, writing the new city file directly.
- 2026-10-29 — Turin routes restored: the 13 district walks from Turin 2.0A (every city stop on one walk, only
  Casa Martini off-route) had been left behind — 2.1/2.2 were built on 2.0, and the migration copied only tours
  from 2.0A. city.json `routes` now = 2.0A's. Nothing else differed between 2.0A and Turin. Launcher opens the
  default city (`cities/index.json` "default": turin); "Cities" button in the panel goes to `#all`.
- 2026-10-29 — Turin station guides rewritten (all 161): one strong opening paragraph, then up to 2–3 more only
  where there is something to say; sources line now names real sources instead of report file names. Written
  from the Turin reports only. tools/build_city.py now keeps written guide entries and marks generated ones
  `draft` (Kon's guide-text rule is in its docstring).
- 2026-10-29 — Turin guides rewritten again to Paris depth: main stops 3–4 paragraphs (what you see, story,
  context, practical), minor stops 1–3. Adds historical context beyond the reports (general history, flagged
  where uncertain); fixes Teatro Regio façade (Benedetto Alfieri, not Juvarra).
- 2026-10-29 — Plovdiv added (concrete/0.3), built from claude/plovdiv-sites.md rather than migrating legacy 1.0: 72 stops (A concrete/socialist, B pass-by, C thinkers), 7 day trips, 10 area walks, 7 tours, Study (intro, socialist Plovdiv, violence and memory, thinkers, passes), station guides written by hand from the reports. Base drawn from Natural Earth (the old 1.0 base lacked the Maritsa). Register rows with no coordinates are not mapped yet (see project 00-status).
- 2026-10-30 — concrete/0.3 fixed in place: "What to show" has one cutoff. Each kind keeps its top N by score; the Show
  slider sets every kind's N ("score X+"), the per-kind sliders under it ("By kind", with All/None) fine-tune it
  ("Custom mix"); total shown = sum of the kind sliders + starred. Available in Sites and Custom. Replaces Custom's
  kind checkboxes and the Custom-only per-kind toggle (old saved plans are read in). The hidden filter no longer
  applies in Curated. Custom walks drawn like planned routes: the city's route colours, solid, haloed when picked.
- 2026-11-05 — Vatra Dornei files copied into Git from the live artifact (they were only published). Cluj-Napoca added
  (cities/cluj): 15-stop half-afternoon loop + 9 stops off it (Mănăștur, Makovecz church, Gheorgheni, two markets,
  the €50k automatic toilet); guides hand-written from the Oct 2026 research report; base without the river.
- 2026-11-06 — Vatra Dornei street map: OSM via Overpass (Kon downloaded on phone; raw/vatra-dornei-osm.json), add_streets.py + OSM town rivers (Bistrița, Dorna…) replacing Natural Earth inside the town box.
- 2026-11-05 — Cluj street map: OSM named streets from GitHub `madeincluj/street-names` (2013, ODbL; 830 streets).
  shared/glyphs.json gains a trimmed 256-511 range (ă ș ț ş ţ ő ű ł) for all three fonts, so Romanian and Hungarian
  street names render; Turin checked unchanged.
- 2026-11-05 — Launcher opens the last city opened on this device (localStorage `konmap.last`), else the city list;
  cities/index.json "default" no longer used. concrete/0.3 popup: links (Maps, Transit, Citymapper, Photos) first, then
  Star/Fade, then Read the guide; the 'Walk route X from here' button is gone (walks start from the route card). Guide
  and event panels: links before Star/Fade too.
- 2026-11-06 — concrete/0.3 gains a 'church' kind (cross glyph, indigo, filterable), fixed in place; Turin, Plovdiv
  checked unchanged. Rome added (cities/rome), replacing the legacy single-page Rome: 134 stops (59 religious by era,
  27 concrete, 26 pass-by, 16 lore, 6 thinkers), 14 area walks, 14 tours incl. the modern church day (main), a second
  modern day and the all-eras day; Study with 6 readings + the research reports. Base from Natural Earth + OSM coast.
- 2026-11-06 — Standalone shareable Vatra Dornei page: `/vatra-dornei/index.html` (repo root, built by tools/make_standalone.py from KonMap; artifact "Vatra Dornei · KonMap", slug 46c5987a-8fc2-43a4-b46f-5ce7e1623cdc). Rebuild it after Vatra Dornei changes. Engine concrete/0.3 synced from the live artifact (popup/legend changes were only published).
- 2026-11-06 — Spanish standalone Vatra Dornei: `/vatra-dornei-es/index.html` (artifact "Vatra Dornei · KonMap (español)", slug df995817-ce30-410c-9254-824d9ea28804). Text in cities/vatra-dornei/es/, interface strings in tools/i18n/es.py; `make_standalone.py vatra-dornei <out> es`. Standalone pages now inline Leaflet (shared/vendor). Both Vatra Dornei pages are built with --sites-first (Sites tab left and open on load; Vatra Dornei only, not KonMap).
- 2026-11-06 — Vatra Dornei classics from the research "Basic and classic sights" (16 stops, list D, routes 9–12, 12 Apostoli optional on route 7) in English and Spanish; base map land extended to 25.95 E / 47.92 N for the monasteries and Rarău. Engine concrete/0.3: new home-pin module (`cc.home` = [{lat,lon,name,note}], house icon, not a site); Vatra Dornei uses it for the hostel. Standalone pages rebuilt.
