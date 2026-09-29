# Milestone 1 — High-impact programmes

Status: implemented in 14d2eda · Versions and URLs checked on 2026-09-29

## Goal

Auto-update the 13 programme pages where a stale version hurts most: Softcatalà's
own language tools and the most downloaded third-party programmes. This
milestone also builds the shared helpers that milestones 2 and 3 reuse.

## Why these programmes

Each page pins a version or a versioned download URL that has gone stale, the
upstream project is active, and a machine-readable source exists. Download
counts are all-time totals from `baixades.softcatala.org`.

## Scope

| Programme | WordPress slug | API route | Downloads | Site → upstream |
|---|---|---|---|---|
| Corrector ortogràfic (general), LibreOffice | `corrector-ortografic-de-catala-general-per-al-libreoffice-i-lapache-openoffice` | `softcatala/dict-ca` | 232k | 3.0.8 → 3.0.9 |
| Corrector ortogràfic (valencià), LibreOffice | `corrector-ortografic-de-catala-valencia-per-al-libreoffice-i-lapache-openoffice` | `softcatala/dict-ca-valencia` | 21k | 3.0.8 → 3.0.9 |
| Diccionari de sinònims | `diccionari-catala-de-sinonims-per-al-libreoffice` | `softcatala/thesaurus` | 96k | 2.3.1 → 2.3.2 |
| Diccionari de partició de mots | `diccionari-catala-de-particio-de-mots` | `softcatala/hyphen` | 20k | 1.5 (current) |
| Corrector (general) per a Mozilla | `corrector-ortografic-de-catala-general-per-a-mozilla` | `mozilla/dict-ca` (existing) | 132k | 3.0.1 → 3.0.8 |
| Corrector (valencià) per a Mozilla | `corrector-ortografic-de-catala-valencia-per-a-mozilla` | `mozilla/dict-ca-valencia` (existing) | 5k | 3.0.6 → 3.0.8 |
| LanguageTool per al Firefox | `corrector-gramatical-en-catala-languagetool-per-al-firefox` | `mozilla/languagetool` | 27k | 1.0.13 → 11.3.1 |
| WinRAR | `winrar` | `winrar` | 320k | 7.11 → 7.23 |
| Adobe Acrobat Reader | `adobe-acrobat-reader` | `adobe-reader` | 278k | 2025.001.20693 → 2026.002.21931 |
| VLC media player | `vlc-media-player` | `vlc` | 185k | none / 3.0.0 → 3.0.24 |
| Audacity | `audacity` | `audacity` | 155k | 3.0.0 → 4.0.0 |
| FileZilla | `filezilla` | `filezilla` | 26k | 3.69.3 → 3.71.1 |
| Subtitle Edit | `subtitle-edit` | `subtitle-edit` | n/a | 3.6.4 → 5.2.0 |

All 13 WordPress posts already exist with these slugs.

## Shared groundwork

Build these first; every provider in the three milestones depends on them.

1. **URL validation.** A helper that sends a HEAD request to each versioned
   binary URL and rejects the result when one does not resolve to a file. When
   validation fails the route returns `404 NoData`, so WordPress keeps the rows
   it already has. Landing pages (HTML) are allowed only for rows declared as
   such. Some hosts reject HEAD requests, so fall back to a GET with
   `Range: bytes=0-0` before treating a URL as broken.
2. **GitHub releases helper.** `get_github_release(repo)` in `utils`, reading
   `https://api.github.com/repos/<repo>/releases/latest`. It returns the tag,
   the version with the tag prefix stripped, and the assets with their sizes.
   Asset sizes come from the API, so no HEAD request is needed for them. The
   helper sends `Authorization: Bearer $GITHUB_TOKEN` when that variable is set.
3. **AMO helper.** `get_amo_addon(id_or_slug)` reading
   `https://addons.mozilla.org/api/v5/addons/addon/<id>/` and returning
   `current_version.version`.
4. **Static rows.** A way to declare rows that never change (store links,
   landing pages) next to the discovered ones. See constraint 1 below.

## Providers

### Softcatalà dictionaries (4 pages)

One module, `softcatala/`, with one route `/softcatala/<program>`.

| Route | Repository | Assets to publish |
|---|---|---|
| `dict-ca` | `Softcatala/catalan-dict-tools` | `ca.<v>.oxt` |
| `dict-ca-valencia` | `Softcatala/catalan-dict-tools` | `ca-valencia.<v>.oxt` |
| `thesaurus` | `Softcatala/sinonims-cat` | `thesaurus-ca.oxt` |
| `hyphen` | `jaumeortola/hyphen-ca` | `hyph-ca.oxt`, `hyph_ca_ES.dic` (version label `<v> (TXT)`) |

All rows use `os='multiplataforma'`, `arch='generic'`.

### Mozilla add-ons (3 pages, plus a fix for 6 existing ones)

- Register the two extra slugs against the existing `mozilla/dict-ca` and
  `mozilla/dict-ca-valencia` routes. The index accepts several entries with the
  same `api` and a different `wp`.
- Add `mozilla/languagetool` (AMO slug `languagetool`). The row links to the
  add-on page, as it does today.
- Fill `download_version` from the AMO helper in every add-on route. Today the
  six existing add-on routes return an empty version, which the site renders as
  `1.0`.

### WinRAR

- Version from the Scoop manifest `Extras/bucket/winrar.json`.
- URL: `https://www.rarlab.com/rar/winrar-x64-<version without dots>ca.exe`.
- The Catalan build can appear later than the English one, so validation is
  mandatory here. If the Catalan file is missing, return `NoData`.
- Static row: Android, `https://play.google.com/store/apps/details?id=com.rarlab.rar&hl=ca`.

### Adobe Acrobat Reader

- Version from
  `https://rdc.adobe.io/reader/products?lang=ca&site=enterprise&os=Windows%2011&country=ES&nativeOs=Windows%2010&api_key=dc-get-adobereader-cdn`
  with the header `x-api-key: dc-get-adobereader-cdn`. It returns the Catalan
  build, for example `26.002.21931`.
- URL: `https://ardownload3.adobe.com/pub/adobe/reader/win/AcrobatDC/<digits>/AcroRdrDC<digits>_ca_ES.exe`,
  where `<digits>` is the version without dots (`2600221931`). This resolves
  for the current version.
- Display version: prefix `20` (`2026.002.21931`) to match the page.
- Only the 32-bit Catalan installer exists; the 64-bit pattern returns 404.
- Risk: this is the key Adobe's own download site uses, not a documented API.
  Validation protects the page if it stops working.

### VLC

- Version from the Scoop manifest `Extras/bucket/vlc.json`.
- URLs on `https://get.videolan.org/vlc/<v>/`: `win64/vlc-<v>-win64.exe`,
  `win32/vlc-<v>-win32.exe`, `macosx/vlc-<v>-universal.dmg`. These are mirror
  redirector pages that return HTML, so declare them as landing rows.
- Static rows: Linux (`https://www.videolan.org/vlc/#download`), Android and iOS
  store links from the current page.

### Audacity

- GitHub `audacity/audacity`, tag prefix `Audacity-`.
- Assets: `audacity-win-<v>-x86_64.msi`, `audacity-win-<v>-arm64.msi`,
  `audacity-macOS-<v>-universal.dmg`, `audacity-linux-<v>-x86_64.AppImage`.
- Do not use Scoop for the version: it still reports 3.7.9.

### FileZilla

- Version from the Scoop manifest `Extras/bucket/filezilla.json`.
- Direct links carry a token that expires; the links on the page today return
  an HTML page. Publish landing rows to
  `https://filezilla-project.org/download.php?show_all=1` for Windows, macOS
  and Linux, with the discovered version.

### Subtitle Edit

- GitHub `SubtitleEdit/subtitleedit`, tag prefix `v`.
- Assets: `SubtitleEdit-Windows-x64-Setup.exe`, `SubtitleEdit-Windows-ARM64.zip`,
  `SubtitleEdit-macOS-x64.dmg`, `SubtitleEdit-macOS-ARM64.dmg`,
  `SubtitleEdit-linux-x64.flatpak`.
- Asset names carry no version, so the URL must use the tag
  (`releases/download/<tag>/...`), not `releases/latest/download/`.

## Constraints

1. **WordPress replaces every row.** `SC_Downloads_Updater::update_program`
   overwrites the whole `baixada` field, so a provider must return the static
   rows too or they disappear from the page.
2. **Allowed values.** `download_os`: `windows`, `osx`, `linux`, `ios`,
   `android`, `multiplataforma`, `web`. `arquitectura`: `generic`, `x86`,
   `x86_64`, `arm`. macOS rows with `x86_64` and `arm` render as "Intel" and
   "Apple Silicon".
3. **Response time.** WordPress gives each route 30 seconds (5 seconds until
   the `wp-softcatala` change is deployed). Aim for cold responses under 5
   seconds anyway: take sizes from the GitHub API, and run validation requests
   in parallel.
4. **Every route is registered by hand** in `handler.py`, and the module must
   be imported there for `add_program` to run.
5. **Tests must not use the network.** The Docker build runs `pytest`, so
   parsing is tested against fixtures, as `tests/test_ubuntu.py` does.

## Acceptance criteria

- Each route returns the rows described above with the upstream version.
- Every versioned binary URL in a response resolves to a file.
- A failing upstream produces `404 NoData`, not a 500.
- Cold responses take less than 5 seconds, and never more than 30.
- `wp sc update-downloads --dry-run` lists the 13 pages with the new versions.
- Static rows present on the pages today are still there after an update.

## Known issues in existing providers (not part of this milestone)

Recorded here so they are not lost. They affect pages that were already
auto-updated. The fix for `tor` and `libreoffice/*` is described in
`00-fix-tor-and-libreoffice.md`.

| Provider | Problem | State |
|---|---|---|
| `tor` | Returned 500 after upstream renamed its keys. | Fixed |
| `libreoffice/*` (5 routes) | Returned 500; the `old/latest/` listing is empty. Then timed out: files were checked one after another. | Fixed; files are checked in parallel and the build is looked up once |
| `digikam` | Windows and macOS file names gained a `Qt5`/`Qt6` part. | Fixed: new names, Intel and Apple Silicon rows |
| `krita` | The macOS image is now `krita-<v>-signed.dmg`. | Fixed |
| `kdenlive` | macOS has one image per architecture; the Linux page moved. | Fixed: both images, and the AppImage for Linux |
| `gcompris` | No 32-bit Windows or macOS build upstream any more. | Rows removed |
| `opensuse` | Leap 16 replaced the DVD image with an offline installer. | Fixed |
| `mozilla/firefox`, `firefox-valencia`, `thunderbird` | No 32-bit Linux build upstream; the 64-bit row used `os='linux_64'`. | 32-bit row removed; 64-bit row is `linux` / `x86_64` |
| `calibre` | No 32-bit Windows build upstream. | Row removed |
| `osmand` | Returned 500; its source server is down. | Provider removed; the page no longer exists on the site |
| `mozilla/thunderbird-langpack-ca` | Served the Firefox language pack. | Fixed: the pack of the released Thunderbird, from archive.mozilla.org |
| `mozilla/thunderbird-langpack-ca-valencia` | Served the Firefox language pack. Upstream has had no Valencian pack since Thunderbird 91. | Provider removed; the page should be archived |
| `mozilla/firefox-langpack-*` | Served the newest pack on addons.mozilla.org, which is the one of the beta and does not install on the release. | Fixed: the pack of the released Firefox, from archive.mozilla.org |

The providers fixed for broken links now validate their URLs, so a renamed
file produces `404 NoData` and not a broken link.
