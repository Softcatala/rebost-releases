# Milestone 0 — Fix the Tor Browser and LibreOffice providers

Status: implemented in e4df6f5 · Failures reproduced and URLs checked on 2026-09-29

## Goal

Make the `tor` and `libreoffice/*` routes return data again, so the six pages
they feed resume their daily updates. Make both providers fail cleanly when
upstream changes again.

## Current state

| | Tor Browser | LibreOffice |
|---|---|---|
| Routes | `tor` | `libreoffice/libreoffice`, `helppack-ca`, `helppack-ca-valencia`, `langpack-ca`, `langpack-ca-valencia` |
| Response | HTTP 500 | HTTP 500 |
| Exception | `KeyError: 'linux64'` in `tor/__init__.py`, line 20 | `TypeError: 'NoneType' object is not subscriptable` in `libreoffice/__init__.py`, line 18 |
| Page shows | 12.5.6 | 26.2.6 |
| Newest stable upstream | 15.0.23 | 26.8.0 |
| Links on the page | All five desktop links return 404 | Installers work; the Linux link returns 404 |

WordPress did not detect the failure. The updater ignored the HTTP status, the
500 body is not valid JSON, and it reported "No versions to update" as a
success. The pages kept the rows from the last good run. This is fixed in
`wp-softcatala` (see "Outside this repository"), pending deployment.

## Tor Browser

### Cause

Tor renamed the platform keys in
`https://aus1.torproject.org/torbrowser/update_3/release/downloads.json`.

| Key the code reads | Key in the feed today |
|---|---|
| `linux64` | `linux-x86_64` |
| `linux32` | `linux-i686` |
| `macos` | `macos` |
| `win64` | `win64` |
| `win32` | `win32` |

### Fix

1. Read `linux-x86_64` and `linux-i686` instead of `linux64` and `linux32`.
2. Build the rows from a table of `(feed key, os, arch)` and skip a platform
   whose key is missing, instead of indexing each key directly. A renamed or
   dropped platform then removes one row, not the whole page.
3. Return `None` when no desktop row could be built, so the route answers
   `404 NoData`.

### Rows to publish

Every URL below resolves for 15.0.23.

| os | arch | URL (from the feed, `downloads.<key>.ALL.binary`) |
|---|---|---|
| `windows` | `x86_64` | `tor-browser-windows-x86_64-portable-15.0.23.exe` |
| `windows` | `x86` | `tor-browser-windows-i686-portable-15.0.23.exe` |
| `osx` | `generic` | `tor-browser-macos-15.0.23.dmg` |
| `linux` | `x86_64` | `tor-browser-linux-x86_64-15.0.23.tar.xz` |
| `linux` | `x86` | `tor-browser-linux-i686-15.0.23.tar.xz` |
| `android` | `generic` | `https://play.google.com/store/apps/details?id=org.torproject.torbrowser` (static) |

The Windows files are named "portable", but they are the installers Tor
publishes for Windows; there is no other Windows build in the feed.

### Optional

The same directory has one feed per Android architecture, for example
`download-android-aarch64.json`, with a direct APK link. The page could offer
the APK next to the Google Play link. This is an addition, not part of the fix.

## LibreOffice

### Cause

The provider finds the version by reading the directory listing at
`https://downloadarchive.documentfoundation.org/libreoffice/old/latest/win/x86/`
and matching an `.msi` file name. The `latest` directory still exists but its
platform folders are empty, so `__get_latest_version` returns `None` and the
caller crashes.

### Fix

1. **Find the version** in the listing at
   `https://download.documentfoundation.org/libreoffice/stable/`. It contains
   one folder per released version (`25.8.7`, `26.2.5`, `26.2.6`, `26.8.0`).
   Take the highest. The Scoop manifest for LibreOffice uses the same source.
2. **Find the build number** in the listing at
   `https://downloadarchive.documentfoundation.org/libreoffice/old/`. Take the
   highest folder that starts with the version (`26.8.0.3` for `26.8.0`).
3. **Keep publishing archive URLs**, built as they are today from the
   four-part build number.
4. Return `None` when either step finds nothing, so the route answers
   `404 NoData`.

### Why two listings

- The archive cannot be used alone. It also holds release candidates of
  versions that are not released yet: `26.8.1.1` is there today, and 26.8.1 is
  not in `stable/`.
- The stable mirror cannot be used alone without a cost. It only keeps current
  versions, so its links stop working after a few months. Archive links are
  permanent, which is why the LibreOffice page still downloads today after the
  provider failed. Tor's links are not permanent, and that page has no working
  desktop link.
- The archive lags behind `stable/`. On 2026-10-04 `stable/` listed 26.8.1
  while the archive held only its first release candidate, `26.8.1.1`, with
  most files missing, and every route answered `404 NoData`. Until the
  archive build resolves, the routes publish the same files from
  `stable/<version>/`, and switch to the archive once it has them.
- The two are the same files. `stable/26.8.0/.../LibreOffice_26.8.0_Win_x86-64.msi`
  and `old/26.8.0.3/.../LibreOffice_26.8.0.3_Win_x86-64.msi` have the same
  SHA-256.

### Rows to publish

`<b>` is the build number (`26.8.0.3`). The display version stays three-part
(`26.8.0`). All paths are under
`https://downloadarchive.documentfoundation.org/libreoffice/old/<b>/`.

**`libreoffice/libreoffice`**

| os | arch | Path | State |
|---|---|---|---|
| `windows` | `x86_64` | `win/x86_64/LibreOffice_<b>_Win_x86-64.msi` | Existing |
| `windows` | `x86` | `win/x86/LibreOffice_<b>_Win_x86.msi` | Existing |
| `windows` | `arm` | `win/aarch64/LibreOffice_<b>_Win_aarch64.msi` | New |
| `osx` | `x86_64` | `mac/x86_64/LibreOffice_<b>_MacOS_x86-64.dmg` | Existing |
| `osx` | `arm` | `mac/aarch64/LibreOffice_<b>_MacOS_aarch64.dmg` | New |
| `linux` | `x86_64` | `deb/x86_64/LibreOffice_<b>_Linux_x86-64_deb.tar.gz`, version label `<v> (DEB)` | Replaces the broken link |
| `linux` | `x86_64` | `rpm/x86_64/LibreOffice_<b>_Linux_x86-64_rpm.tar.gz`, version label `<v> (RPM)` | New |

**`libreoffice/helppack-ca` and `helppack-ca-valencia`** (`<l>` is `ca` or
`ca-valencia`)

| os | arch | Path |
|---|---|---|
| `windows` | `x86_64` | `win/x86_64/LibreOffice_<b>_Win_x86-64_helppack_<l>.msi` |
| `windows` | `x86` | `win/x86/LibreOffice_<b>_Win_x86_helppack_<l>.msi` |
| `windows` | `arm` | `win/aarch64/LibreOffice_<b>_Win_aarch64_helppack_<l>.msi` |
| `linux` | `x86_64` | `deb/x86_64/LibreOffice_<b>_Linux_x86-64_deb_helppack_<l>.tar.gz` |

**`libreoffice/langpack-ca` and `langpack-ca-valencia`**

| os | arch | Path |
|---|---|---|
| `osx` | `x86_64` | `mac/x86_64/LibreOffice_<b>_MacOS_x86-64_langpack_<l>.dmg` |
| `osx` | `arm` | `mac/aarch64/LibreOffice_<b>_MacOS_aarch64_langpack_<l>.dmg` |
| `linux` | `x86_64` | `deb/x86_64/LibreOffice_<b>_Linux_x86-64_deb_langpack_<l>.tar.gz` |

One URL of each kind was checked and resolves for `26.8.0.3`: installer
(Windows, macOS ARM, deb), help pack (Windows) and language pack (macOS ARM,
deb). The remaining combinations follow the same naming in the listing.

### The Linux link

Today the Linux row points to
`https://www.libreoffice.org/download/download/?type=deb-x86_64&lang=<l>`,
which returns 404. The tables above replace it with direct package links. If a
landing page is preferred, `https://www.libreoffice.org/download/` resolves.

### Decision needed: which branch to offer

LibreOffice maintains two branches at once. Today `stable/` has 26.8.0 (newer
branch) and 26.2.6 (older branch, published after 26.8.0).

| Option | Page would show | Note |
|---|---|---|
| Highest version (recommended) | 26.8.0 | Deterministic, and what libreoffice.org offers first |
| Most recently published | 26.2.6 | What the old `latest` folder did; the version can go down when the older branch gets a fix |
| Older branch | 26.2.6 | The Document Foundation's suggestion for conservative deployments |

The fix above implements the first option. The second explains why the page
shows 26.2.6 today and not 26.8.0.

## Both providers

1. **No unhandled exceptions.** A provider returns `None` when upstream data
   is missing or has an unexpected shape. The routes in `handler.py` already
   turn `None` into `404 NoData`.
2. **Catch what is left.** Wrap the provider call in each route so an
   unexpected exception is logged and answered with `404 NoData`. The `ubuntu`
   module already does this inside `get`.
3. **Do not cache failures.** `get` is wrapped in a five-minute `TTLCache`.
   Check that a `None` result is not served from the cache for five minutes
   after upstream recovers, or accept that delay explicitly.
4. **Tests from fixtures.** Store a copy of `downloads.json` and of the two
   directory listings under `tests/`, and test the parsing against them. Add
   one test per provider for the broken input: a feed without the Linux keys,
   and an empty listing. The Docker build runs the tests, so they must not use
   the network.

## Acceptance criteria

- `/tor` returns 200 with version 15.0.23 or newer and six rows.
- The five `/libreoffice/*` routes return 200 with the highest version in
  `stable/`.
- Every binary URL in the responses resolves to a file.
- A feed without the expected keys, or an empty listing, produces
  `404 NoData` and a log line.
- `wp sc update-downloads --program=tor --dry-run` and
  `--program=libreoffice --dry-run` list the new versions.
- After the real run, the Tor Browser page has working desktop links.

## Outside this repository

Done in `wp-softcatala`, in `SC_Downloads_Updater`, not yet deployed:

- A response that is not 2xx, or whose body is not a JSON list, counts as a
  failure. The programme keeps its rows, is counted as failed, and the daily
  run logs its name.
- Each route is given 30 seconds to answer, up from 5.

Neither is required for the fix here, but with them a future break is visible
the next day.

## Not covered here

- **OsmAnd map.** The route fails because `gent.softcatala.org/albert/mapa/`
  returns 502. That is a server problem, and the maps were from August 2020
  before it. It needs a decision on whether the map is still maintained.
- **Providers that publish 404 links** (digiKam, Krita, Kdenlive, GCompris,
  openSUSE, calibre, 32-bit Linux for Firefox and Thunderbird). They are listed
  in milestone 1 and are addressed by the URL validation helper defined there.
