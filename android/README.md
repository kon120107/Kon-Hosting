# KonMap Android app

A full-screen wrapper around `konmap/`. It works offline and updates its map data by itself.

- **Contents:** the build copies `konmap/` into the app (minus `raw/`, `tools/`, notes and `curation.json`),
  plus the map libraries and fonts the engine would otherwise load from the web (`app/src/main/assets/vendor/web/`,
  stored under their original URLs and answered from the app when the engine asks for them).
- **Updates:** when opened (and at most once an hour after that), the app asks GitHub for the list of files in
  `main` with their Git hashes, downloads from the Pages site the `konmap/` files that differ, checks each against
  its hash and swaps it in. A bar then offers *Reload*. No network: it keeps what it has.
  So: edit `konmap/` and push as usual; no new app build is needed. New engine versions travel the same way.
- **New build** only when the app itself changes: any push touching `android/` runs
  `.github/workflows/konmap-android.yml`, which publishes `KonMap-<n>.apk` under Releases.
- **Signing:** `android/konmap.jks`, password in the workflow. Public on purpose: the app never installs
  anything by itself, so the key only matters for APKs you install by hand from this repo's Releases.
  Don't lose it: Android only installs an update signed with the same key.
- **If the library versions in an engine change,** add the new files under `vendor/web/<host>/<path>`;
  until then the app loads them from the web the first time.
