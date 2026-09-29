import json
from pathlib import Path

import tor

FIXTURES = Path(__file__).parent / 'fixtures'


def parse(feed):
    # never hit the network for the file size
    import utils
    utils.get_content_size = lambda url: "1024"
    return tor.parse(feed)


def test_parse_builds_all_platforms():
    feed = json.loads((FIXTURES / 'tor_downloads.json').read_text())

    rows = parse(feed)

    assert {(r['download_os'], r['arquitectura']) for r in rows} == {
        ('linux', 'x86_64'), ('linux', 'x86'), ('osx', 'generic'),
        ('windows', 'x86_64'), ('windows', 'x86'), ('android', 'generic'),
    }
    assert all(r['download_version'] == feed['version'] for r in rows)
    linux = [r for r in rows if r['download_os'] == 'linux' and r['arquitectura'] == 'x86_64']
    assert linux[0]['download_url'].endswith('tor-browser-linux-x86_64-%s.tar.xz' % feed['version'])


def test_parse_skips_missing_platform():
    feed = json.loads((FIXTURES / 'tor_downloads.json').read_text())
    del feed['downloads']['linux-x86_64']

    rows = parse(feed)

    assert len(rows) == 5


def test_parse_without_desktop_keys_returns_none():
    assert parse({'version': '1.0', 'downloads': {'linux64': {}}}) is None
