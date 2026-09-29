from types import SimpleNamespace

import pytest

import utils
from providers import calibre, mozilla, opensuse
from providers.kde import digikam, gcompris, kdenlive, krita
from utils import BrokenUrl


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Every url resolves and no size is looked up."""
    def check(urls):
        return {u: '1024' for u in urls}

    monkeypatch.setattr(utils, 'check_urls', check)
    monkeypatch.setattr(opensuse, 'check_urls', check)
    monkeypatch.setattr(utils, 'get_content_size', lambda url: '1024')


def urls(rows):
    return [r['download_url'] for r in rows]


def platforms(rows):
    return [(r['download_os'], r['arquitectura']) for r in rows]


def test_digikam_uses_the_qt_names():
    rows = digikam.build('9.1.0')

    assert urls(rows)[:3] == [
        'https://download.kde.org/stable/digikam/9.1.0/digiKam-9.1.0-Qt6-Win64.exe',
        'https://download.kde.org/stable/digikam/9.1.0/digiKam-9.1.0-Qt5-MacOS-x86_64.pkg',
        'https://download.kde.org/stable/digikam/9.1.0/digiKam-9.1.0-Qt6-MacOS-arm64.pkg',
    ]
    assert platforms(rows) == [('windows', 'x86_64'), ('osx', 'x86_64'), ('osx', 'arm'), ('linux', 'generic')]


def test_krita_macos_is_the_signed_image():
    rows = krita.build('5.3.4')

    assert 'https://download.kde.org/stable/krita/5.3.4/krita-5.3.4-signed.dmg' in urls(rows)
    assert [r['download_os'] for r in rows] == ['windows', 'osx', 'linux', 'android']


def test_kdenlive_has_a_build_per_mac_and_an_appimage():
    rows = kdenlive.build('26.08.1')

    assert urls(rows) == [
        'https://download.kde.org/stable/kdenlive/26.08/windows/kdenlive-26.08.1.exe',
        'https://download.kde.org/stable/kdenlive/26.08/macOS/kdenlive-26.08.1-x86_64.dmg',
        'https://download.kde.org/stable/kdenlive/26.08/macOS/kdenlive-26.08.1-arm64.dmg',
        'https://download.kde.org/stable/kdenlive/26.08/linux/kdenlive-26.08.1-x86_64.AppImage',
    ]


def test_gcompris_offers_no_32_bit_windows_nor_macos():
    rows = gcompris.build('26.2')

    assert platforms(rows) == [('windows', 'x86_64'), ('linux', 'generic'), ('android', 'generic')]
    assert not [u for u in urls(rows) if 'win32' in u or 'Darwin' in u]


def test_opensuse_leap_is_the_offline_installer():
    rows = opensuse.build('16.0')

    assert urls(rows) == [
        'https://download.opensuse.org/distribution/leap/16.0/offline/Leap-16.0-offline-installer-x86_64.install.iso',
        'https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-DVD-x86_64-Current.iso',
    ]
    assert [r['download_version'] for r in rows] == ['16.0', 'Tumbleweed']


def test_calibre_offers_no_32_bit_windows(monkeypatch):
    feed = SimpleNamespace(entries=[SimpleNamespace(id='calibre-9.15')])
    monkeypatch.setattr(calibre.feedparser, 'parse', lambda url: feed)

    rows = calibre.get.__wrapped__()

    assert 'https://calibre-ebook.com/dist/win32' not in urls(rows)
    assert 'https://calibre-ebook.com/dist/win64' in urls(rows)


@pytest.mark.parametrize("program,product,lang", [
    ('firefox', 'firefox', 'ca'),
    ('firefox-valencia', 'firefox', 'ca-valencia'),
    ('thunderbird', 'thunderbird', 'ca'),
])
def test_mozilla_offers_only_64_bit_linux(monkeypatch, program, product, lang):
    monkeypatch.setattr(mozilla, '__get_version', lambda url, key: '156.0.1')

    rows = mozilla.get.__wrapped__(program)
    linux = [r for r in rows if r['download_os'].startswith('linux')]

    assert platforms(linux) == [('linux', 'x86_64')]
    assert urls(linux) == [f'https://download.mozilla.org/?product={product}-156.0.1-SSL&os=linux64&lang={lang}']


@pytest.mark.parametrize("program,product,lang", [
    ('firefox-langpack-ca', 'firefox', 'ca'),
    ('firefox-langpack-ca-valencia', 'firefox', 'ca-valencia'),
    ('thunderbird-langpack-ca', 'thunderbird', 'ca'),
])
def test_language_pack_is_the_one_of_the_release(monkeypatch, program, product, lang):
    monkeypatch.setattr(mozilla, '__get_version', lambda url, key: '156.0.1')

    rows = mozilla.get.__wrapped__(program)

    assert urls(rows) == [f'https://archive.mozilla.org/pub/{product}/releases/156.0.1/linux-x86_64/xpi/{lang}.xpi']
    assert platforms(rows) == [('multiplataforma', 'generic')]
    assert rows[0]['download_version'] == '156.0.1'


def test_dictionaries_still_come_from_the_add_on_site(monkeypatch):
    monkeypatch.setattr(mozilla, 'get_amo_addon', lambda addon: {'version': '3.0.8', 'url': '', 'size': 12})

    rows = mozilla.get.__wrapped__('dict-ca')

    assert urls(rows) == ['https://addons.mozilla.org/firefox/downloads/latest/3369/addon-3369-latest.xpi']


def test_thunderbird_has_no_valencian_language_pack():
    assert mozilla.get('thunderbird-langpack-ca-valencia') is None
    assert 'paquet-catala-valencia-per-al-thunderbird' not in [p['wp'] for p in utils.get_all_programs()]


def test_osmand_is_not_offered():
    assert 'osmand' not in [p['api'] for p in utils.get_all_programs()]


@pytest.mark.parametrize("build,version", [
    (digikam.build, '9.1.0'),
    (krita.build, '5.3.4'),
    (kdenlive.build, '26.08.1'),
    (gcompris.build, '26.2'),
    (opensuse.build, '16.0'),
])
def test_renamed_file_is_not_published(monkeypatch, build, version):
    def broken(urls):
        raise BrokenUrl('gone')

    monkeypatch.setattr(utils, 'check_urls', broken)
    monkeypatch.setattr(opensuse, 'check_urls', broken)

    with pytest.raises(BrokenUrl):
        build(version)
