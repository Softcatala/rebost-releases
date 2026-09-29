import re

from utils import add_program, cached_route, download_data, get_github_release

# Each programme is an entry in `programs`; see docs/milestones/02-tier-2-github-releases.md.
#
#   wp          WordPress slug
#   repo        GitHub repository
#   tag_prefix  stripped from the tag to get the display version
#   version_from (optional) {'asset': regex with one group}, for repositories
#               whose tag is not the version the assets use
#   assets      rows found in the release: a regular expression that must match
#               exactly one asset name ({v} is the version), plus os, arch and
#               an optional label appended to the version
#   static      rows that never change (store links, landing pages); they are
#               returned too because WordPress replaces every row


def asset(pattern, os, arch='generic', label=''):
    return {'pattern': pattern, 'os': os, 'arch': arch, 'label': label}


def static(url, os, arch='generic', version=None):
    """version None means the discovered version"""
    return {'url': url, 'os': os, 'arch': arch, 'version': version}


programs = {
    'librecad': {
        'wp': 'librecad',
        'repo': 'LibreCAD/LibreCAD',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^LibreCAD-v{v}-win64-msvc\.exe$', 'windows', 'x86_64'),
            asset(r'^LibreCAD-v{v}-msvc\.exe$', 'windows', 'x86'),
            asset(r'^LibreCAD-v{v}\.dmg$', 'osx', 'x86_64'),
            asset(r'^LibreCAD-v{v}-arm64\.dmg$', 'osx', 'arm'),
            asset(r'^LibreCAD-v{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
    },
    'openshot': {
        'wp': 'openshot',
        'repo': 'OpenShot/openshot-qt',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^OpenShot-v{v}-x86_64\.exe$', 'windows', 'x86_64'),
            asset(r'^OpenShot-v{v}-x86\.exe$', 'windows', 'x86'),
            asset(r'^OpenShot-v{v}-x86_64\.dmg$', 'osx', 'x86_64'),
            asset(r'^OpenShot-v{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
        'static': [static('https://www.openshot.org/download/', 'linux')],
    },
    'gnucash': {
        'wp': 'gnucash',
        'repo': 'Gnucash/gnucash',
        'tag_prefix': '',
        'assets': [
            asset(r'^gnucash-{v}\.setup\.exe$', 'windows', 'x86_64'),
            asset(r'^Gnucash-Intel-{v}-1\.dmg$', 'osx', 'x86_64'),
            asset(r'^Gnucash-Arm-{v}-1\.dmg$', 'osx', 'arm'),
        ],
    },
    'exelearning': {
        'wp': 'exelearning',
        'repo': 'exelearning/exelearning',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^eXeLearning-Setup-{v}\.exe$', 'windows'),
            asset(r'^eXeLearning-{v}-universal\.dmg$', 'osx'),
            asset(r'^exelearning_{v}_amd64\.deb$', 'linux', 'x86_64', ' (DEB)'),
            asset(r'^exelearning-{v}\.x86_64\.rpm$', 'linux', 'x86_64', ' (RPM)'),
        ],
    },
    'musescore': {
        'wp': 'musescore',
        'repo': 'musescore/MuseScore',
        'tag_prefix': 'v',
        # asset names carry a build number: MuseScore-Studio-4.7.5.260831071-...
        'assets': [
            asset(r'^MuseScore-Studio-{v}\.\d+-x86_64\.msi$', 'windows', 'x86_64'),
            asset(r'^MuseScore-Studio-{v}\.\d+\.dmg$', 'osx'),
            asset(r'^MuseScore-Studio-{v}\.\d+-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
        'static': [
            static('https://play.google.com/store/apps/details?id=com.musescore.playerlite', 'android', version=''),
            static('https://itunes.apple.com/app/apple-store/id835731296', 'ios', version=''),
        ],
    },
    'stellarium': {
        'wp': 'stellarium',
        'repo': 'Stellarium/stellarium',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^stellarium-{v}-qt6-win64\.exe$', 'windows', 'x86_64'),
            asset(r'^stellarium-{v}-qt6-arm64\.exe$', 'windows', 'arm'),
            asset(r'^Stellarium-{v}-qt6-macOS\.zip$', 'osx'),
            asset(r'^Stellarium-{v}-qt6-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
    },
    'gramps': {
        'wp': 'gramps',
        'repo': 'gramps-project/gramps',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^GrampsAIO-{v}--1_win64\.exe$', 'windows', 'x86_64'),
            asset(r'^Gramps-Intel-{v}-1\.dmg$', 'osx', 'x86_64'),
            asset(r'^Gramps-Arm-{v}-1\.dmg$', 'osx', 'arm'),
        ],
    },
    'darktable': {
        'wp': 'darktable',
        'repo': 'darktable-org/darktable',
        'tag_prefix': 'release-',
        'assets': [
            asset(r'^darktable-{v}-win64\.exe$', 'windows', 'x86_64'),
            asset(r'^darktable-{v}-x86_64\.dmg$', 'osx', 'x86_64'),
            asset(r'^darktable-{v}-arm64\.dmg$', 'osx', 'arm'),
            asset(r'^Darktable-{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
        'static': [static(
            'https://software.opensuse.org/download.html?project=graphics:darktable:stable&package=darktable',
            'linux')],
    },
    'sigil': {
        'wp': 'sigil',
        'repo': 'Sigil-Ebook/Sigil',
        'tag_prefix': '',
        'assets': [
            asset(r'^Sigil-{v}-Windows-x64-Setup\.exe$', 'windows', 'x86_64'),
            asset(r'^Sigil\.app-{v}-Mac-x86_64\.txz$', 'osx', 'x86_64'),
            asset(r'^Sigil\.app-{v}-Mac-arm64\.txz$', 'osx', 'arm'),
            asset(r'^Sigil-{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
    },
    'geany': {
        'wp': 'geany',
        'repo': 'geany/geany',
        'tag_prefix': '',
        # the tag is 2.1.0 and the assets use 2.1
        'version_from': {'asset': r'^geany-([\d.]+)_setup\.exe$'},
        'assets': [
            asset(r'^geany-{v}_setup\.exe$', 'windows'),
            asset(r'^geany-{v}_osx\.dmg$', 'osx', 'x86_64'),
            asset(r'^geany-{v}_osx_arm64\.dmg$', 'osx', 'arm'),
        ],
    },
    'cryptomator': {
        'wp': 'cryptomator',
        'repo': 'cryptomator/cryptomator',
        'tag_prefix': '',
        'assets': [
            asset(r'^Cryptomator-{v}-x64\.exe$', 'windows', 'x86_64'),
            asset(r'^Cryptomator-{v}-x64\.msi$', 'windows', 'x86_64', ' (MSI)'),
            asset(r'^Cryptomator-{v}-x64\.dmg$', 'osx', 'x86_64'),
            asset(r'^Cryptomator-{v}-arm64\.dmg$', 'osx', 'arm'),
            asset(r'^cryptomator-{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
            asset(r'^cryptomator-{v}-aarch64\.AppImage$', 'linux', 'arm'),
        ],
        'static': [
            static('https://static.cryptomator.org/android/fdroid/repo?fingerprint='
                   'F7C3EC3B0D588D3CB52983E9EB1A7421C93D4339A286398E71D7B651E8D8ECDD', 'android', version='F-Droid'),
            static('https://play.google.com/store/apps/details?id=org.cryptomator&hl=en', 'android',
                   version='Google Play'),
            static('https://apps.apple.com/us/app/cryptomator/id1560822163', 'ios', version=''),
        ],
    },
    'joplin': {
        'wp': 'joplin',
        'repo': 'laurent22/joplin',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^Joplin-Setup-{v}\.exe$', 'windows'),
            # the Intel build has no architecture in its name
            asset(r'^Joplin-{v}\.dmg$', 'osx', 'x86_64'),
            asset(r'^Joplin-{v}-arm64\.dmg$', 'osx', 'arm'),
            asset(r'^Joplin-{v}\.AppImage$', 'linux'),
        ],
        'static': [
            static('https://play.google.com/store/apps/details?id=net.cozic.joplin', 'android', version=''),
            static('https://itunes.apple.com/us/app/joplin/id1315599797', 'ios', version=''),
        ],
    },
    'qbittorrent': {
        'wp': 'qbittorrent',
        'repo': 'qbittorrent/qBittorrent',
        'tag_prefix': 'release-',
        # the lt20 variants are built against libtorrent 2.0
        'assets': [
            asset(r'^qbittorrent_{v}_x64_setup\.exe$', 'windows', 'x86_64'),
            asset(r'^qbittorrent-{v}_x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
    },
    'veracrypt': {
        'wp': 'veracrypt',
        'repo': 'veracrypt/VeraCrypt',
        'tag_prefix': 'VeraCrypt_',
        'assets': [
            asset(r'^VeraCrypt_Setup_x64_{v}\.msi$', 'windows', 'x86_64'),
            asset(r'^VeraCrypt_Setup_arm64_{v}\.msi$', 'windows', 'arm'),
            asset(r'^VeraCrypt_{v}\.dmg$', 'osx'),
            asset(r'^VeraCrypt-{v}-x86_64\.AppImage$', 'linux', 'x86_64'),
        ],
    },
    'drawio': {
        'wp': 'diagrams',
        'repo': 'jgraph/drawio-desktop',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^draw\.io-{v}-windows-installer\.exe$', 'windows', 'x86_64'),
            asset(r'^draw\.io-universal-{v}\.dmg$', 'osx'),
            asset(r'^drawio-x86_64-{v}\.AppImage$', 'linux', 'x86_64', ' (AppImage)'),
            asset(r'^drawio-amd64-{v}\.deb$', 'linux', 'x86_64', ' (DEB)'),
        ],
        'static': [static('https://app.diagrams.net/', 'web')],
    },
    'onionshare': {
        'wp': 'onionshare',
        'repo': 'onionshare/onionshare',
        'tag_prefix': 'v',
        'assets': [
            asset(r'^OnionShare-win64-{v}\.msi$', 'windows', 'x86_64'),
            asset(r'^OnionShare-{v}\.dmg$', 'osx'),
            asset(r'^OnionShare-{v}\.flatpak$', 'linux', 'x86_64'),
        ],
        'static': [
            static('https://play.google.com/store/apps/details?id=org.onionshare.android', 'android',
                   version='Google Play'),
            static('https://f-droid.org/packages/org.onionshare.android.fdroid/', 'android', version='F-Droid'),
            static('https://apps.apple.com/gb/app/onionshare/id1601890129', 'ios', version=''),
        ],
    },
    'jpexs': {
        'wp': 'jpexs',
        'repo': 'jindrapetrik/jpexs-decompiler',
        'tag_prefix': 'version',
        'assets': [
            asset(r'^ffdec_{v}\.msi$', 'windows'),
            asset(r'^ffdec_{v}\.pkg$', 'osx'),
            asset(r'^ffdec_{v}\.deb$', 'linux'),
        ],
    },
}

for __name, __config in programs.items():
    add_program('github', f'github/{__name}', __config['wp'])


@cached_route()
def get(program):
    if program not in programs:
        return None

    config = programs[program]

    return build(config, get_github_release(config['repo'], config['tag_prefix']))


def find_version(config, release):
    """The version shown on the page: the tag without its prefix, unless the
    assets say otherwise."""
    source = config.get('version_from')
    if not source:
        return release['version']

    found = {m.group(1) for name in release['assets']
             if (m := re.search(source['asset'], name))}
    if len(found) != 1:
        raise ValueError(f"version_from matched {sorted(found)} in release {release['tag']}")

    return found.pop()


def find_asset(release, pattern, version):
    regex = re.compile(pattern.replace('{v}', re.escape(version)), re.IGNORECASE)
    found = [name for name in release['assets'] if regex.search(name)]

    if len(found) != 1:
        raise ValueError(f"{pattern!r} matched {found} in release {release['tag']}, expected exactly one")

    return release['assets'][found[0]]


def build(config, release):
    version = find_version(config, release)

    rows = []
    for a in config['assets']:
        found = find_asset(release, a['pattern'], version)
        rows.append(download_data(
            f"{version}{a['label']}",
            url=found['url'],
            size=found['size'],
            arch=a['arch'],
            os=a['os'],
        ))

    for s in config.get('static', []):
        rows.append(download_data(
            version if s['version'] is None else s['version'],
            url=s['url'],
            arch=s['arch'],
            os=s['os'],
        ))

    return rows
