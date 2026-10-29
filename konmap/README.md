# KonMap

Master copy of the city maps. This folder is the source of truth and the backup (Git keeps every version).
The claude.ai artifact and the GitHub Pages copy are both just this folder, published.

## Where it lives

| What | Where |
|---|---|
| Source + backup | `kon120107/Kon-Hosting`, folder `konmap/` |
| Live artifact (the one you open) | **KonMap** — slug in `REGISTRY.md` |
| Public copy | GitHub Pages: `/konmap/` in Kon-Hosting |

## Layout

```
konmap/
  index.html                 launcher: lists cities; index.html#turin opens Turin
  cities/index.json          which cities exist and which engine each uses
  cities/<id>/city.json      everything about one city (see "City file")
  cities/<id>/base.json      the city's base map
  cities/<id>/reports.json   research reports for the Study tab (optional)
  cities/<id>/curation.json  hand-written input for tools/build_city.py (new cities; Turin has none)
  engines/<name>/<ver>/      one engine version (the map program)
  shared/glyphs.json         map label fonts, shared by all engines
  tools/                     build a city file from research, base maps, migrate old pages (see tools/README.md)
  REGISTRY.md                live artifacts, rules, change log
```

## Rules (for Claude too)

1. **An engine exists once.** No city holds its own copy of the map program. City files hold only data.
2. **Several engines are allowed** (e.g. a trip engine, a long-stay engine). Each city names one in
   `cities/index.json` and in its `city.json` `meta.engine`, e.g. `concrete/0.3`.
3. **Engine versions:** small fixes edit the current version folder in place (Git keeps the old one).
   A change that could break or change other cities gets a new folder (`concrete/0.4`); cities move to it
   one by one, deliberately.
4. **No variant copies** (no more 2.0A next to 2.0). An experiment is a switch inside the engine, tried in the
   *KonMap Lab* artifact, logged, then kept or removed.
5. **Only the artifacts in `REGISTRY.md` are edited.** Everything else is legacy and read-only.
6. Every change: edit here → commit → republish the artifact from this folder → add a line to the change log.
7. **The map is for using.** No development notes, version strings or build remarks in the page; those go in the
   change log and the project docs.

## City file (`city.json`)

| Key | What |
|---|---|
| `meta` | `id`, `name`, `engine`, `source` (`kon` = curated by Kon), `updated` |
| `cfg` | city settings the engine reads: base map file, reports list, metro lines |
| `cc` | city config: bounds, labels, colours, help note |
| `data` | `sights` (all places) and `offmap` |
| `guide` | the long text per place |
| `routes` | planned area walks |
| `tours` | curated tours by era and by theme |
| `offids`, `evdata`, `paths` | day trips, events, optional route paths |

## Two content layers (planned)

- **Curated (Kon):** everything in these files. Implicitly `source: kon`.
- **Community:** places, reviews, comments and photos added by invited people. These will live in the artifact's
  database (not in Git), each row with author id and date, and the engine shows them labelled as such.
  Sign-in covers Kon and people he invites.
