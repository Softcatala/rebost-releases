import pytest

import adobe
import audacity
import filezilla
import subtitleedit
import utils
import vlc
import winrar
import softcatala
from utils import BrokenUrl, parse_amo_addon, parse_github_release


def release(tag, names, prefix=''):
    return parse_github_release({
        'tag_name': tag,
        'assets': [{'name': n, 'size': 1000, 'browser_download_url': f'https://x/{tag}/{n}'} for n in names],
    }, prefix)


class Resp:
    def __init__(self, status=200, headers=None):
        self.status_code = status
        self.headers = headers or {}

    def close(self):
        pass


def test_parse_github_release_strips_prefix():
    r = release('Audacity-4.0.0', ['a.msi'], 'Audacity-')

    assert r['version'] == '4.0.0'
    assert r['tag'] == 'Audacity-4.0.0'
    assert r['assets']['a.msi'] == {'url': 'https://x/Audacity-4.0.0/a.msi', 'size': 1000}


def test_parse_amo_addon():
    js = {'url': 'https://amo/x', 'current_version': {'version': '3.0.8', 'file': {'size': 12}}}

    assert parse_amo_addon(js) == {'version': '3.0.8', 'url': 'https://amo/x', 'size': 12}


def test_check_urls_accepts_files_and_reports_size(monkeypatch):
    monkeypatch.setattr(utils.requests, 'head',
                        lambda url, **kw: Resp(200, {'Content-Length': '99', 'Content-Type': 'application/x-msdownload'}))

    assert utils.check_urls(['https://a/x.exe']) == {'https://a/x.exe': '99'}


def test_check_urls_rejects_html_and_missing(monkeypatch):
    monkeypatch.setattr(utils.requests, 'head', lambda url, **kw: Resp(200, {'Content-Type': 'text/html'}))
    monkeypatch.setattr(utils.requests, 'get', lambda url, **kw: Resp(404))

    with pytest.raises(BrokenUrl):
        utils.check_urls(['https://a/x.exe'])


def test_check_urls_falls_back_to_ranged_get(monkeypatch):
    monkeypatch.setattr(utils.requests, 'head', lambda url, **kw: Resp(405))
    seen = {}

    def get(url, **kw):
        seen.update(kw['headers'])
        return Resp(206, {'Content-Range': 'bytes 0-0/4242', 'Content-Type': 'application/octet-stream'})

    monkeypatch.setattr(utils.requests, 'get', get)

    assert utils.check_urls(['https://a/x.exe']) == {'https://a/x.exe': '4242'}
    assert seen == {'Range': 'bytes=0-0'}


def test_cached_route_does_not_cache_failures():
    calls = []

    @utils.cached_route()
    def get(program):
        calls.append(program)
        if len(calls) == 1:
            raise RuntimeError('boom')
        return [1]

    assert get('x') is None
    assert get('x') == [1]
    assert get('x') == [1]
    assert len(calls) == 2


def test_softcatala_dictionary():
    r = release('v3.0.9', ['ca.3.0.9.oxt', 'ca-valencia.3.0.9.oxt'], 'v')

    rows = softcatala.build(r, softcatala.programs['dict-ca'][2])

    assert [(x['download_version'], x['download_url'], x['download_os'], x['arquitectura']) for x in rows] == [
        ('3.0.9', 'https://x/v3.0.9/ca.3.0.9.oxt', 'multiplataforma', 'generic')]


def test_softcatala_hyphen_has_txt_row():
    r = release('v1.5', ['hyph-ca.oxt', 'hyph_ca_ES.dic'], 'v')

    rows = softcatala.build(r, softcatala.programs['hyphen'][2])

    assert [x['download_version'] for x in rows] == ['1.5', '1.5 (TXT)']


def test_softcatala_missing_asset_fails():
    with pytest.raises(ValueError):
        softcatala.build(release('v3.0.9', ['other'], 'v'), softcatala.programs['dict-ca'][2])


def test_winrar_builds_catalan_url_and_keeps_static_row(monkeypatch):
    monkeypatch.setattr(winrar, 'check_urls', lambda urls: {u: '10' for u in urls})

    rows = winrar.build('7.23')

    assert rows[0]['download_url'] == 'https://www.rarlab.com/rar/winrar-x64-723ca.exe'
    assert rows[1]['download_os'] == 'android'


def test_winrar_fails_when_catalan_build_is_missing(monkeypatch):
    def missing(urls):
        raise BrokenUrl('missing')

    monkeypatch.setattr(winrar, 'check_urls', missing)

    with pytest.raises(BrokenUrl):
        winrar.build('7.24')


def test_adobe(monkeypatch):
    monkeypatch.setattr(adobe, 'check_urls', lambda urls: {u: '10' for u in urls})
    js = {'products': {'reader': [{'version': '26.002.21931'}], 'dcPro': []}}

    rows = adobe.build(adobe.parse_version(js))

    assert rows[0]['download_version'] == '2026.002.21931'
    assert rows[0]['download_url'] == (
        'https://ardownload3.adobe.com/pub/adobe/reader/win/AcrobatDC/2600221931/AcroRdrDC2600221931_ca_ES.exe')


def test_adobe_without_products_raises():
    with pytest.raises((KeyError, IndexError)):
        adobe.parse_version({'products': {'reader': []}})


def test_vlc_has_landing_and_static_rows():
    rows = vlc.build('3.0.24')

    assert {r['download_os'] for r in rows} == {'windows', 'osx', 'linux', 'android', 'ios'}
    assert 'https://get.videolan.org/vlc/3.0.24/win64/vlc-3.0.24-win64.exe' in [r['download_url'] for r in rows]


def test_filezilla_rows_are_landing_pages():
    rows = filezilla.build('3.71.1')

    assert {r['download_url'] for r in rows} == {filezilla.landing}
    assert {r['download_os'] for r in rows} == {'windows', 'osx', 'linux'}


def test_audacity():
    v = '4.0.0'
    names = [f'audacity-win-{v}-x86_64.msi', f'audacity-win-{v}-arm64.msi',
             f'audacity-macOS-{v}-universal.dmg', f'audacity-linux-{v}-x86_64.AppImage']

    rows = audacity.build(release('Audacity-4.0.0', names, 'Audacity-'))

    assert len(rows) == 4
    assert {r['download_version'] for r in rows} == {v}


def test_subtitle_edit_uses_tag_url():
    names = ['SubtitleEdit-Windows-x64-Setup.exe', 'SubtitleEdit-Windows-ARM64.zip',
             'SubtitleEdit-macOS-x64.dmg', 'SubtitleEdit-macOS-ARM64.dmg',
             'SubtitleEdit-linux-x64.flatpak']

    rows = subtitleedit.build(release('v5.2.0', names, 'v'))

    assert len(rows) == 5
    assert rows[0]['download_version'] == '5.2.0'
    assert '/v5.2.0/' in rows[0]['download_url']
