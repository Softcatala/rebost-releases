# Milestone 2 — GitHub releases provider

Status: implemented in 8dde1a9 · Versions and assets checked on 2026-09-29

## Goal

Auto-update 17 programme pages from GitHub releases with one generic provider.
Adding a programme after this milestone means adding a configuration entry, not
a module.

## Depends on

Milestone 1: the GitHub releases helper, URL validation and static rows.

## Why these programmes

Each page pins versioned download URLs, most of them years old, and each
upstream publishes its installers as GitHub release assets.

## Scope

Ordered by all-time downloads. Pages showing "n/a" have no counter data.

| Programme | WordPress slug | Repository | Downloads | Site → upstream |
|---|---|---|---|---|
| LibreCAD | `librecad` | `LibreCAD/LibreCAD` | 15k | 2.2.1 → 2.2.1.5 |
| OpenShot | `openshot` | `OpenShot/openshot-qt` | 15k | 3.1.1 → 4.0.1 |
| GnuCash | `gnucash` | `Gnucash/gnucash` | 10k | 2.6.7 → 5.17 |
| eXeLearning | `exelearning` | `exelearning/exelearning` | 6k | 2.4.1 → 4.0.5 |
| MuseScore | `musescore` | `musescore/MuseScore` | 4k | 3.6.2 → 4.7.5 |
| Stellarium | `stellarium` | `Stellarium/stellarium` | 3k | 0.14.3 → 26.3 |
| Gramps | `gramps` | `gramps-project/gramps` | 2k | 4.2.2 → 6.0.8 |
| darktable | `darktable` | `darktable-org/darktable` | 2k | 3.8.0 → 5.6.1 |
| Sigil | `sigil` | `Sigil-Ebook/Sigil` | 1k | 0.8.7 → 2.8.1 |
| Geany | `geany` | `geany/geany` | 1k | 1.27 → 2.1 |
| Cryptomator | `cryptomator` | `cryptomator/cryptomator` | n/a | 1.13.0 → 1.19.3 |
| Joplin | `joplin` | `laurent22/joplin` | n/a | 2.3.5 → 3.7.21 |
| qBittorrent | `qbittorrent` | `qbittorrent/qBittorrent` | n/a | 4.4.0 → 5.2.4 |
| VeraCrypt | `veracrypt` | `veracrypt/VeraCrypt` | n/a | 1.23 → 1.26.29 |
| draw.io | `diagrams` | `jgraph/drawio-desktop` | n/a | 24.7.8 → 31.5.3 |
| OnionShare | `onionshare` | `onionshare/onionshare` | n/a | 2.6.2 → 2.6.5 |
| JPEXS | `jpexs` | `jindrapetrik/jpexs-decompiler` | n/a | 15.0.0 → 26.3.0 |

Sigil, Geany and JPEXS are the lowest-value entries and can be dropped without
affecting the rest.

## Design

One module, `github/`, with one route `/github/<program>` and API paths such as
`github/librecad`. Each programme is a configuration entry:

```python
'librecad': {
    'wp': 'librecad',
    'repo': 'LibreCAD/LibreCAD',
    'tag_prefix': 'v',
    'assets': [
        {'pattern': r'-win64-msvc\.exe$', 'os': 'windows', 'arch': 'x86_64'},
        {'pattern': r'-arm64\.dmg$', 'os': 'osx', 'arch': 'arm'},
    ],
    'static': [],
}
```

- `pattern` is a regular expression matched against asset names. Exactly one
  asset must match; zero or several is an error for that programme.
- `label` (optional) is appended to the version, for example `5.17 (MSI)`, when
  two rows share the same OS and architecture.
- `version_from` (optional) overrides how the display version is read, for
  repositories whose tag is not the version (see MuseScore and Geany).

## Asset patterns

Asset names as published in the latest release. `<v>` is the version.

| Programme | Tag | Assets to publish |
|---|---|---|
| LibreCAD | `v<v>` | `-win64-msvc.exe`, `-msvc.exe` (32-bit), `.dmg` (Intel), `-arm64.dmg`, `-x86_64.AppImage` |
| OpenShot | `v<v>` | `-x86_64.exe`, `-x86.exe`, `-x86_64.dmg`, `-x86_64.AppImage` |
| GnuCash | `<v>` | `gnucash-<v>.setup.exe`, `Gnucash-Intel-<v>-1.dmg`, `Gnucash-Arm-<v>-1.dmg` |
| eXeLearning | `v<v>` | `eXeLearning-Setup-<v>.exe`, `eXeLearning-<v>-universal.dmg`, `exelearning_<v>_amd64.deb`, `exelearning-<v>.x86_64.rpm` |
| MuseScore | `v<v>` | `-x86_64.msi`, `.dmg`, `-x86_64.AppImage` |
| Stellarium | `v<v>` | `-qt6-win64.exe`, `-qt6-arm64.exe`, `-qt6-macOS.zip`, `-qt6-x86_64.AppImage` |
| Gramps | `v<v>` | `GrampsAIO-<v>--1_win64.exe`, `Gramps-Intel-<v>-1.dmg`, `Gramps-Arm-<v>-1.dmg` |
| darktable | `release-<v>` | `-win64.exe`, `-x86_64.dmg`, `-arm64.dmg`, `-x86_64.AppImage` |
| Sigil | `<v>` | `-Windows-x64-Setup.exe`, `-Mac-x86_64.txz`, `-Mac-arm64.txz`, `-x86_64.AppImage` |
| Geany | `<v>.0` | `geany-<v>_setup.exe`, `geany-<v>_osx.dmg`, `geany-<v>_osx_arm64.dmg` |
| Cryptomator | `<v>` | `-x64.exe`, `-x64.msi` (label `MSI`), `-x64.dmg`, `-arm64.dmg`, `-x86_64.AppImage`, `-aarch64.AppImage` |
| Joplin | `v<v>` | `Joplin-Setup-<v>.exe`, `Joplin-<v>.dmg`, `Joplin-<v>-arm64.DMG`, `Joplin-<v>.AppImage` |
| qBittorrent | `release-<v>` | `qbittorrent_<v>_x64_setup.exe`, `qbittorrent-<v>_x86_64.AppImage` |
| VeraCrypt | `VeraCrypt_<v>` | `VeraCrypt_Setup_x64_<v>.msi`, `VeraCrypt_Setup_arm64_<v>.msi`, `VeraCrypt_<v>.dmg`, `VeraCrypt-<v>-x86_64.AppImage` |
| draw.io | `v<v>` | `draw.io-<v>-windows-installer.exe`, `draw.io-universal-<v>.dmg`, `drawio-x86_64-<v>.AppImage`, `drawio-amd64-<v>.deb` |
| OnionShare | `v<v>` | `OnionShare-win64-<v>.msi`, `OnionShare-<v>.dmg`, `OnionShare-<v>.flatpak` |
| JPEXS | `version<v>` | `ffdec_<v>.msi`, `ffdec_<v>.pkg`, `ffdec_<v>.deb` |

## Static rows to keep

These rows are on the pages today and the provider must return them.

| Programme | Rows |
|---|---|
| MuseScore | iOS and Android store links |
| Cryptomator | F-Droid repository, Google Play, iOS App Store |
| Joplin | Android and iOS store links |
| OnionShare | Google Play, F-Droid, iOS App Store |
| draw.io | Web, `https://app.diagrams.net/` |
| darktable | Linux packages, `https://software.opensuse.org/download.html?project=graphics:darktable:stable&package=darktable` |
| OpenShot | Linux landing page, `https://www.openshot.org/download/` |

## Special cases

- **MuseScore.** Asset names include a build number
  (`4.7.5.260831071`). Publish the tag version (`4.7.5`) as the display version.
- **Geany.** The tag is `2.1.0` and the assets use `2.1`. Read the version from
  the asset name.
- **eXeLearning.** The page points to the old repository
  `exelearning/iteexe`, which stopped at 2.9. Version 4 is a rewrite; confirm
  that the page text still describes it before enabling.
- **macOS builds without an architecture in the name** (LibreCAD `.dmg`,
  Joplin `.dmg`) are Intel builds: publish them as `x86_64`.
- **qBittorrent** no longer publishes a macOS build or a 32-bit Windows build
  on GitHub. Those rows disappear from the page.
- **Pre-releases.** `releases/latest` excludes pre-releases and drafts, so no
  extra filtering is needed.

## Constraints

The five constraints in milestone 1 apply. Two matter most here:

- **Rate limit.** Unauthenticated GitHub API calls are limited to 60 per hour
  per IP address. This milestone adds 17 calls per refresh, on top of 5 from
  milestone 1. The daily run fits, but a dry run followed by a real run within
  the hour can exceed the limit. Setting `GITHUB_TOKEN` in the container raises
  it to 5,000.
- **Pattern drift.** Upstream projects rename assets. A pattern that matches
  nothing must fail that programme only and return `404 NoData`.

## Acceptance criteria

- `/github/<program>` returns rows for all 17 programmes.
- A pattern that matches zero or several assets fails that programme without
  affecting the others.
- Sizes come from the GitHub API; the route makes no HEAD request for
  GitHub-hosted assets.
- Tests cover asset matching and version extraction against stored release
  fixtures, including the MuseScore and Geany cases.
- `wp sc update-downloads --program=github --dry-run` lists the 17 pages.
- Adding an eighteenth programme needs only a configuration entry.

## Not included

- **QMapShack**: its releases have no assets.
- **X-Moto**: 0.6.3 is both the page version and the latest release.
- **Buzz** and **Primitive FTPd**: their pages link to `releases/latest`, which
  never goes stale.
