import json
from pathlib import Path

import pytest

import utils
from utils import BrokenUrl
from vendors import blender, linuxmint, omegat, opera, poedit, qgis, signal, sumatrapdf, virtualbox, zotero

FIXTURES = Path(__file__).parent / 'fixtures' / 'vendors'


def text(name):
    return (FIXTURES / name).read_text()


@pytest.fixture(autouse=True)
def all_urls_resolve(monkeypatch):
    """Validation is tested in test_tier1; here every url resolves."""
    def check(urls):
        return {u: '1024' for u in urls}

    for module in (utils, opera, virtualbox, sumatrapdf, blender, linuxmint, poedit, signal, zotero, omegat):
        if hasattr(module, 'check_urls'):
            monkeypatch.setattr(module, 'check_urls', check)


def urls(rows):
    return [r['download_url'] for r in rows]


def test_virtualbox_finds_build_number_in_sha256sums():
    version = virtualbox.parse_version(text('virtualbox_latest.txt'))

    rows = virtualbox.build(version, text('virtualbox_sha256sums.txt'))

    assert version == '7.2.20'
    assert urls(rows)[:3] == [
        'https://download.virtualbox.org/virtualbox/7.2.20/VirtualBox-7.2.20-175154-Win.exe',
        'https://download.virtualbox.org/virtualbox/7.2.20/VirtualBox-7.2.20-175154-OSX.dmg',
        'https://download.virtualbox.org/virtualbox/7.2.20/VirtualBox-7.2.20-175154-macOSArm64.dmg',
    ]
    assert rows[3]['download_os'] == 'linux'
    assert [(r['download_os'], r['arquitectura']) for r in rows[1:3]] == [('osx', 'x86_64'), ('osx', 'arm')]


def test_virtualbox_missing_file_fails():
    with pytest.raises(ValueError):
        virtualbox.build('7.2.20', 'abc *SDKRef.pdf\n')


def test_virtualbox_garbage_version_fails():
    with pytest.raises(ValueError):
        virtualbox.parse_version('<html>error</html>')


def test_signal_picks_x64_exe_and_dmg_not_zip():
    rows = signal.build(text('signal_latest.yml'), text('signal_latest_mac.yml'))

    assert urls(rows)[:2] == [
        'https://updates.signal.org/desktop/signal-desktop-win-x64-8.28.0.exe',
        'https://updates.signal.org/desktop/signal-desktop-mac-universal-8.28.0.dmg',
    ]
    assert {r['download_os'] for r in rows} == {'windows', 'osx', 'android', 'ios'}
    assert {r['download_version'] for r in rows} == {'8.28.0'}


def test_signal_without_expected_files_fails():
    with pytest.raises(ValueError):
        signal.build('version: 9.0.0\nfiles:\n  - url: other.exe\n', text('signal_latest_mac.yml'))


def test_signal_feed_without_version_fails():
    with pytest.raises(ValueError):
        signal.parse('<html>not found</html>')


def test_qgis_version_from_text_and_from_code():
    body = text('qgis_version.txt')

    assert qgis.parse_version(body) == '4.2.2'
    assert qgis.parse_version('#QGIS Version 30822|x') == '3.8.22'
    with pytest.raises(ValueError):
        qgis.parse_version('<html>')


def test_qgis_rows_are_landing_pages():
    rows = qgis.build('4.2.2')

    assert set(urls(rows)) == {'https://qgis.org/download/'}


def test_zotero_reads_version_per_row():
    locations = [
        'https://download.zotero.org/client/release/10.0.3/Zotero-10.0.3_x64_setup.exe',
        'https://download.zotero.org/client/release/10.0.4/Zotero-10.0.4.dmg',
        'https://download.zotero.org/client/release/10.0.3/Zotero-10.0.3_linux-x86_64.tar.xz',
    ]

    rows = zotero.build(locations)

    assert [r['download_version'] for r in rows] == ['10.0.3', '10.0.4', '10.0.3']
    assert urls(rows) == locations


def test_zotero_without_redirect_fails():
    with pytest.raises(ValueError):
        zotero.build(['', '', ''])


def test_omegat_finds_files_in_the_folder_listing():
    rows = omegat.build('6.1.1', text('omegat_rss.xml'))

    assert [(r['download_os'], r['arquitectura']) for r in rows] == [
        ('windows', 'x86_64'), ('windows', 'arm'), ('linux', 'x86_64'), ('multiplataforma', 'generic')]
    assert urls(rows)[0].endswith('/OmegaT_6.1.1_Windows_64_signed.exe/download')


def test_omegat_missing_required_file_fails():
    with pytest.raises(ValueError):
        omegat.build('7.0.0', text('omegat_rss.xml'))


def test_linuxmint_skips_lmde_cycles():
    cycles = json.loads(text('linuxmint_eol.json'))

    assert linuxmint.latest_release([{'cycle': 'lmde7'}] + cycles) == cycles[0]['cycle']
    with pytest.raises(ValueError):
        linuxmint.latest_release([{'cycle': 'lmde7'}])


def test_linuxmint_iso_url():
    rows = linuxmint.build('22.3')

    assert urls(rows) == ['https://mirrors.kernel.org/linuxmint/stable/22.3/linuxmint-22.3-cinnamon-64bit.iso']


def test_pattern_providers():
    assert urls(opera.build('136.0.6008.52')) == [
        'https://get.geo.opera.com/pub/opera/desktop/136.0.6008.52/win/Opera_136.0.6008.52_Setup_x64.exe',
        'https://get.geo.opera.com/pub/opera/desktop/136.0.6008.52/win/Opera_136.0.6008.52_Setup.exe',
        'https://get.geo.opera.com/pub/opera/desktop/136.0.6008.52/mac/Opera_136.0.6008.52_Setup.dmg',
    ]
    assert [r['arquitectura'] for r in sumatrapdf.build('3.6.1')] == ['x86_64', 'x86', 'arm']
    assert 'Blender5.2/blender-5.2.2-windows-x64.msi' in urls(blender.build('5.2.2'))[0]
    rows = poedit.build('3.9.1')
    assert rows[0]['download_url'] == 'https://download.poedit.net/Poedit-3.9.1-setup.exe'
    assert {r['download_url'] for r in rows[1:]} == {'https://poedit.net/download'}


def test_renamed_file_produces_no_data(monkeypatch):
    def broken(urls):
        raise BrokenUrl('gone')

    monkeypatch.setattr(utils, 'check_urls', broken)
    monkeypatch.setattr(opera, 'get_scoop', lambda url: {'version': '1.0'})

    assert opera.get() is None
