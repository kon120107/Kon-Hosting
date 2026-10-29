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
| Copenhagen, Paris, Rome, Athens, Plovdiv | — | legacy single-page artifacts; migrate one by one |

## Legacy artifacts (read-only, to be deleted when Kon says)

Turin Concrete Map 1.0, 1.0A, 2.0, 2.0A, 2.1, 2.2 · Copenhagen 1.1, 1.2 · Paris 4.1 · Rome 1.0 · Athens 1.0 ·
Plovdiv 1.0 · Apps (HTML holder prototype). Old GitHub Pages folders `turin-concrete-map/`, `paris-concrete-map/`.

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
