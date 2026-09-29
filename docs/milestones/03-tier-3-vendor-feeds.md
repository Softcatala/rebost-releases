# Milestone 3 — Vendor feeds

Status: implemented in a58fdab · Versions and feeds checked on 2026-09-29

## Goal

Auto-update 11 programme pages whose upstream does not publish installers on
GitHub releases. Each one needs its own small provider, following the pattern
of the existing Scoop-based modules (`gimp`, `sevenzip`, `transmission`).

## Depends on

Milestone 1: URL validation and static rows. Milestone 2 is not required.

## Why these programmes

Every page pins a version that is years old, and several link to installers
that are older than the version shown. They cost more per programme than
milestone 2, because each has its own source and URL pattern.

## Scope

| Programme | WordPress slug | API route | Downloads | Site → upstream |
|---|---|---|---|---|
| Opera | `opera` | `opera` | 8k | 62 → 136.0.6008.52 |
| VirtualBox | `virtualbox` | `virtualbox` | 8k | 6.1.30 → 7.2.20 |
| Sumatra PDF | `sumatra-pdf` | `sumatrapdf` | 4k | 3.5.2 → 3.6.1 |
| Blender | `blender` | `blender` | 2k | 2.68 → 5.2.2 |
| Linux Mint | `linux-mint` | `linuxmint` | 2k | 18 → 22.3 |
| Poedit | `poedit` | `poedit` | 2k | 1.8.7 → 3.9.1 |
| KeePass | `keepass` | `keepass` | 2k | 1.31 → 2.61.1 |
| Signal | `signal-private-messenger` | `signal` | 1k | 1.40.1 (in the URL) → 8.28.0 |
| Zotero | `zotero` | `zotero` | n/a | 5.0.80 → 10.0.x |
| OmegaT | `omegat` | `omegat` | n/a | 5.7.0 → 6.1.1 |
| QGIS | `qgis` | `qgis` | n/a | 3.8.2 → 4.2.2 |

## Providers

Scoop manifests live at
`https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/<name>.json`
and are read with the existing `get_scoop` helper.

### VirtualBox

- Version: `https://download.virtualbox.org/virtualbox/LATEST-STABLE.TXT`.
- File names include a build number, read from
  `https://download.virtualbox.org/virtualbox/<v>/SHA256SUMS`:
  `VirtualBox-<v>-<build>-Win.exe`, `-OSX.dmg` (Intel), `-macOSArm64.dmg`.
- Static row: Linux, `https://www.virtualbox.org/wiki/Linux_Downloads`.

### Blender

- Version: Scoop `blender`.
- URLs on `https://download.blender.org/release/Blender<major>.<minor>/`:
  `blender-<v>-windows-x64.msi`, `blender-<v>-macos-arm64.dmg`,
  `blender-<v>-linux-x64.tar.xz`. All three resolve for 5.2.2.
- There is no Intel macOS build for 5.2.2 (`macos-x64.dmg` returns 404).

### Opera

- Version: Scoop `opera`.
- URLs on `https://get.geo.opera.com/pub/opera/desktop/<v>/`:
  `win/Opera_<v>_Setup_x64.exe`, `win/Opera_<v>_Setup.exe`,
  `mac/Opera_<v>_Setup.dmg`.

### Zotero

- Zotero's redirector gives the version and the file in one request:
  `https://www.zotero.org/download/client/dl?channel=release&platform=<p>`
  with `<p>` in `win-x64`, `mac`, `linux-x86_64`. Read the `Location` header
  without following it.
- Platforms can be on different patch versions on the same day (10.0.4 on
  macOS, 10.0.3 elsewhere), so read the version per row.

### Signal

- `https://updates.signal.org/desktop/latest.yml` (Windows) and
  `latest-mac.yml` (macOS) give the version, file names and sizes.
- Files are served from `https://updates.signal.org/desktop/<file>`.
- Publish `signal-desktop-win-x64-<v>.exe` and, for macOS, the entry ending in
  `.dmg` (`signal-desktop-mac-universal-<v>.dmg`). The other macOS entries are
  `.zip` update packages.
- Parsing YAML needs a new dependency (`pyyaml`) or a regular expression over
  the three fields used.
- Static rows: iOS and Android store links.

### Sumatra PDF

- Version: Scoop `sumatrapdf`.
- URLs on `https://www.sumatrapdfreader.org/dl/rel/<v>/`:
  `SumatraPDF-<v>-64-install.exe`, `SumatraPDF-<v>-install.exe`,
  `SumatraPDF-<v>-arm64-install.exe`.
- Publish the ARM build with `arch='arm'`. The page labels it "32 bits" today.

### OmegaT

- Version: Scoop `omegat`.
- URLs on
  `https://downloads.sourceforge.net/project/omegat/OmegaT%20-%20Standard/OmegaT%20<v>/`.
  The Windows file is `OmegaT_<v>_Windows_64_signed.exe`, which resolves for
  6.1.1. Take the macOS, Linux and "without JRE" names from the SourceForge
  folder listing; they were not checked.

### Poedit

- Version: Scoop `poedit`.
- Windows: `https://download.poedit.net/Poedit-<v>-setup.exe`. This host
  rejects HEAD requests; a ranged GET returns the file.
- macOS and Linux: landing rows to `https://poedit.net/download`.
- The page shows 1.8.7 but its links download 1.4.3.

### QGIS

- Version: the first line of `https://version.qgis.org/version.txt`
  (`#QGIS Version 40202|...` and "The current released version of QGIS is
  4.2.2").
- Installer names are not predictable, so publish landing rows to
  `https://qgis.org/download/` for Windows, macOS and Linux with the
  discovered version.

### Linux Mint

- Version: `get_eol_date('linuxmint')`, field `cycle`.
- URL: `https://mirrors.kernel.org/linuxmint/stable/<v>/linuxmint-<v>-cinnamon-64bit.iso`
  with `get_size=True`. It resolves for 22.3.
- Follows the pattern of the existing `debian` and `opensuse` modules.

### KeePass

- Version: Scoop `keepass`.
- URL: `https://downloads.sourceforge.net/project/keepass/KeePass%202.x/<v>/KeePass-<v>-Setup.exe`.
  It resolves for 2.61.1.
- The page documents KeePass 1.x. Confirm that moving it to 2.x is wanted
  before enabling.

## Constraints

The five constraints in milestone 1 apply. Specific to this milestone:

- **Scoop can lag.** Scoop reported Audacity 3.7.9 when upstream had released
  4.0.0. A provider that reads the version from Scoop publishes what Scoop
  knows, which can be behind.
- **Scoop URLs are for portable builds.** Use Scoop for the version only and
  build installer URLs from the vendor's pattern.
- **Validation is mandatory.** Every URL here is built from a pattern, so a
  vendor renaming a file must produce `404 NoData`, not a broken link.
- **SourceForge answers by client.** It sends the file to a plain HTTP client
  and an HTML page to a browser. Validate with the default `requests` user
  agent.

## Acceptance criteria

- Each of the 11 routes returns rows with the upstream version.
- Every versioned binary URL in a response resolves to a file.
- A failing or changed upstream produces `404 NoData`.
- Cold responses take less than 5 seconds, and never more than 30.
- Tests cover version and file-name parsing against stored fixtures for
  VirtualBox (`SHA256SUMS`), Signal (`latest.yml`), QGIS (`version.txt`) and
  Zotero (the `Location` header).
- `wp sc update-downloads --dry-run` lists the 11 pages.

## Not included

- **Cyberduck, Mp3tag, Advanced Renamer, Bitcoin Core**: a source exists, but
  traffic is low. They can be added later with the same approach.
- **XnView, CCleaner, PDFCreator**: their links never change; only the version
  label would be updated.
- **SeaMonkey**: upstream no longer publishes a Catalan build or language pack.
