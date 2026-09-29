from pathlib import Path

import pytest

import libreoffice
import utils
from utils import BrokenUrl

FIXTURES = Path(__file__).parent / 'fixtures'
STABLE = (FIXTURES / 'libreoffice_stable.html').read_text()
OLD = (FIXTURES / 'libreoffice_old.html').read_text()


def test_highest_stable():
    assert libreoffice.highest_stable(STABLE) == '26.8.0'


def test_highest_build_ignores_release_candidates():
    assert libreoffice.highest_build(OLD, '26.8.0') == '26.8.0.3'
    assert libreoffice.highest_build(OLD, '26.2.6') == '26.2.6.3'


def test_empty_listings():
    assert libreoffice.highest_stable('') is None
    assert libreoffice.highest_build('', '26.8.0') is None


def test_get_returns_none_when_upstream_is_empty(monkeypatch):
    class R:
        text = ''
        def raise_for_status(self): pass

    monkeypatch.setattr(libreoffice.requests, 'get', lambda url, **kwargs: R())

    assert libreoffice.get('libreoffice') is None


# get() keeps what it answers for five minutes, so the tests that need a fresh
# answer call the function behind it
fresh = libreoffice.get.__wrapped__


@pytest.fixture(autouse=True)
def forget_build():
    getattr(libreoffice, '__build').clear()


def listings(monkeypatch):
    """Serves the stored listings and counts how often they are asked for."""
    asked = []

    class R:
        def __init__(self, text): self.text = text
        def raise_for_status(self): pass

    def get(url, **kwargs):
        asked.append(url)
        return R(STABLE if url == libreoffice.stable_url else OLD)

    monkeypatch.setattr(libreoffice.requests, 'get', get)
    monkeypatch.setattr(utils, 'check_urls', lambda urls: {u: '1024' for u in urls})

    return asked


def test_rows_point_to_the_archive(monkeypatch):
    listings(monkeypatch)

    rows = fresh('langpack-ca-valencia')

    assert [r['download_version'] for r in rows] == ['26.8.0'] * 3
    assert rows[0]['download_url'] == (
        'https://downloadarchive.documentfoundation.org/libreoffice/old/26.8.0.3/'
        'mac/x86_64/LibreOffice_26.8.0.3_MacOS_x86-64_langpack_ca-valencia.dmg'
    )


def test_build_is_looked_up_once_for_the_five_routes(monkeypatch):
    asked = listings(monkeypatch)

    for program in ('libreoffice', 'helppack-ca', 'helppack-ca-valencia', 'langpack-ca'):
        assert fresh(program)

    assert asked == [libreoffice.stable_url, libreoffice.archive_url]


def test_files_are_checked_together(monkeypatch):
    listings(monkeypatch)
    calls = []

    def check(urls):
        calls.append(list(urls))
        return {u: '1024' for u in urls}

    monkeypatch.setattr(utils, 'check_urls', check)

    rows = fresh('helppack-ca')

    assert len(calls) == 1
    assert len(calls[0]) == len(rows) == 4


def test_missing_file_publishes_nothing(monkeypatch):
    listings(monkeypatch)

    def broken(urls):
        raise BrokenUrl('gone')

    monkeypatch.setattr(utils, 'check_urls', broken)

    with pytest.raises(BrokenUrl):
        fresh('helppack-ca-valencia')
