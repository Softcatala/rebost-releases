from pathlib import Path

import libreoffice

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

    monkeypatch.setattr(libreoffice.requests, 'get', lambda url: R())

    assert libreoffice.get('libreoffice') is None
