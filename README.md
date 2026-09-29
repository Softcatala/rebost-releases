# rebost-releases

A small web service that finds the latest version of the programs listed on
[Softcatalà's download site](https://baixades.softcatala.org), with a download
link for each platform, and serves them as JSON. The WordPress site calls it to
keep every program page up to date without anyone editing it by hand.

It began as a service for Ubuntu releases and now covers over 70 programs:
Linux distributions, Softcatalà's own language tools, Firefox and LibreOffice
with their Catalan language packs, and general-purpose programs from
VLC to QGIS.

## API

`GET /` lists every program the service knows about:

```json
[
  {"wp": "vlc-media-player", "api": "vlc", "group": "vlc"},
  {"wp": "paquet-catala-per-al-firefox", "api": "mozilla/firefox-langpack-ca", "group": "mozilla"}
]
```

- `wp` is the slug of the program's page in WordPress.
- `api` is the route that returns its downloads.
- `group` is the provider that answers it.

`GET /<api>` returns the downloads of one program, one row per file:

```json
[
  {
    "download_version": "3.0.24",
    "download_url": "https://get.videolan.org/vlc/3.0.24/win64/vlc-3.0.24-win64.exe",
    "download_size": "",
    "arquitectura": "x86_64",
    "download_os": "windows"
  }
]
```

`download_os` is one of `windows`, `osx`, `linux`, `android`, `ios` or
`multiplataforma`. `arquitectura` is `x86_64`, `x86`, `arm` or `generic`.
`download_size` is human-readable (`44.1 MB`) and empty when upstream does not
say.

A route answers `404 NoData` when upstream cannot be reached or a link it
builds no longer resolves to a file. WordPress then keeps what it had instead
of publishing a broken link.

### Routes

| Route | Programs |
|---|---|
| `/ubuntu/<flavor>` | `ubuntu`, `kubuntu`, `xubuntu`, `ubuntu-mate` |
| `/debian`, `/fedora`, `/opensuse`, `/linuxmint` | Linux distributions |
| `/libreoffice/<program>` | `libreoffice`, `langpack-ca`, `langpack-ca-valencia`, `helppack-ca`, `helppack-ca-valencia` |
| `/mozilla/<program>` | `firefox`, `firefox-valencia`, `firefox-langpack-ca`, `firefox-langpack-ca-valencia`, `thunderbird`, `thunderbird-langpack-ca`, `dict-ca`, `dict-ca-valencia`, `languagetool` |
| `/softcatala/<program>` | `dict-ca`, `dict-ca-valencia`, `thesaurus`, `hyphen` (Softcatalà's dictionaries for LibreOffice) |
| `/github/<program>` | `cryptomator`, `darktable`, `drawio`, `exelearning`, `geany`, `gnucash`, `gramps`, `joplin`, `jpexs`, `librecad`, `musescore`, `onionshare`, `openshot`, `qbittorrent`, `sigil`, `stellarium`, `veracrypt` |
| `/<program>` | `7zip`, `adobe-reader`, `audacity`, `blender`, `calibre`, `digikam`, `filezilla`, `gcompris`, `gimp`, `inkscape`, `kdenlive`, `keepass`, `krita`, `notepadplusplus`, `omegat`, `opera`, `poedit`, `qgis`, `signal`, `subtitle-edit`, `sumatrapdf`, `tor`, `transmission`, `virtualbox`, `vlc`, `winrar`, `zotero` |

`GET /` is the full list, with the WordPress slug of each.

## Where the versions come from

Each provider asks the most reliable machine-readable source it can find. In
order of preference:

- the vendor's own update feed (Signal, VirtualBox, OmegaT, Zotero and others)
- the latest GitHub release, which also gives the exact file names and sizes
- the [Scoop](https://scoop.sh) manifests, for programs whose vendor has no feed
- endoflife.date and the Mozilla and addons.mozilla.org APIs

When a download URL is built from a pattern instead of read from upstream, the
service checks that it resolves to a real file (not an HTML page) before
returning it. `docs/milestones/` explains, for each program, where its version
and URLs come from and why.

Results are kept in memory for five minutes (the list of Ubuntu releases for
an hour). Upstream calls time out after three seconds, because WordPress gives
each route five.

## Code layout

```
handler.py         Flask routes
utils/             shared helpers: rows, URL checks, caching, GitHub, Scoop, AMO
providers/         one module per provider
  github.py        the generic GitHub releases provider, one entry per program
  kde/             digiKam, GCompris, Kdenlive, Krita
  ubuntu/          Ubuntu flavours (releases and ISO lookup)
  ...
tests/             pytest, with upstream responses saved in tests/fixtures/
docs/milestones/   what each batch of providers covers, and the sources used
```

All providers live under `providers/`, so none of them can hide a module
of the same name from the standard library or PyPI (`signal`, `github`,
`debian`…).

A provider registers itself when it is imported and exposes `get()`, or
`get(program)` when one route serves several programs:

```python
from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/keepass.json'

add_program("keepass", 'keepass', 'keepass')   # group, api route, WordPress slug


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    url = f"https://downloads.sourceforge.net/project/keepass/KeePass%202.x/{v}/KeePass-{v}-Setup.exe"

    return checked_rows(v, [(url, 'windows', 'generic')])
```

### Adding a program

- **On GitHub, with the installers attached to the release:** add an entry to
  `programs` in `providers/github.py`. Nothing else is needed.
- **Anything else:** add `providers/<name>.py`, import it in `handler.py` and
  add its route there. Keep the parsing in a `build()` that takes the version
  (or the upstream document) so it can be tested against a fixture without
  going to the network.

The slug given to `add_program` must be the one of the program's page in
WordPress.

## Running it

It needs Python 3.14.

```sh
pipenv install --dev
pipenv run pytest tests/
pipenv run python handler.py        # development server on :5000
```

In production it runs under gunicorn in Docker, with one process and eight
threads so the in-memory cache is shared (see `gunicorn.conf.py`):

```sh
docker build -t rebost-releases .   # the build also runs the tests
docker run -p 5000:5000 rebost-releases
```

Set `GITHUB_TOKEN` to raise GitHub's API rate limit. Without it, GitHub allows
60 requests an hour.

Every push to `master` builds `ghcr.io/softcatala/rebost-releases:latest` and
redeploys it.
