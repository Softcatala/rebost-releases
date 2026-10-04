import re

import requests
from cachetools import TTLCache

from utils import REQUEST_TIMEOUT, BrokenUrl, add_program, cached_route, checked_rows

stable_url = 'https://download.documentfoundation.org/libreoffice/stable/'
archive_url = 'https://downloadarchive.documentfoundation.org/libreoffice/old/'

# The five routes publish the same build, so only the first one looks it up
__build = TTLCache(maxsize=1, ttl=300)


@cached_route()
def get(program):
    if program not in __programs:
        return None

    return __programs[program](__latest_build())


def __latest_build():
    if 'latest' not in __build:
        build = __get_latest_build()

        if not build[0]:
            raise ValueError("could not find the latest LibreOffice version")

        __build['latest'] = build

    return __build['latest']


def __rows(latest, entries):
    """latest: (version, build); entries: (os, arch, path, version label suffix)"""
    version, build = latest

    # The archive gets the final build some days after stable/ lists the
    # release, and until then holds only its release candidates. Its links are
    # permanent, so they are preferred; stable/ ones expire with the release.
    if build:
        try:
            return __checked(version, archive_url + build, build, entries)
        except BrokenUrl as e:
            print(f"providers.libreoffice: {build} not in the archive yet, using stable/: {e}")

    return __checked(version, stable_url + version, version, entries)


def __checked(version, base, name, entries):
    # checked in parallel: one after another, seven files take over 8 seconds
    return checked_rows(version, [
        (f"{base}/{path.format(b=name)}", os, arch, label)
        for os, arch, path, label in entries
    ])


def __libreoffice(build):
    return __rows(build, [
        ('windows', 'x86_64', 'win/x86_64/LibreOffice_{b}_Win_x86-64.msi', ''),
        ('windows', 'x86', 'win/x86/LibreOffice_{b}_Win_x86.msi', ''),
        ('windows', 'arm', 'win/aarch64/LibreOffice_{b}_Win_aarch64.msi', ''),
        ('osx', 'x86_64', 'mac/x86_64/LibreOffice_{b}_MacOS_x86-64.dmg', ''),
        ('osx', 'arm', 'mac/aarch64/LibreOffice_{b}_MacOS_aarch64.dmg', ''),
        ('linux', 'x86_64', 'deb/x86_64/LibreOffice_{b}_Linux_x86-64_deb.tar.gz', ' (DEB)'),
        ('linux', 'x86_64', 'rpm/x86_64/LibreOffice_{b}_Linux_x86-64_rpm.tar.gz', ' (RPM)'),
    ])


def __help_pack(build, lang="ca"):
    return __rows(build, [
        ('windows', 'x86_64', f'win/x86_64/LibreOffice_{{b}}_Win_x86-64_helppack_{lang}.msi', ''),
        ('windows', 'x86', f'win/x86/LibreOffice_{{b}}_Win_x86_helppack_{lang}.msi', ''),
        ('windows', 'arm', f'win/aarch64/LibreOffice_{{b}}_Win_aarch64_helppack_{lang}.msi', ''),
        ('linux', 'x86_64', f'deb/x86_64/LibreOffice_{{b}}_Linux_x86-64_deb_helppack_{lang}.tar.gz', ''),
    ])


def __help_pack_valencia(build):
    return __help_pack(build, lang="ca-valencia")


def __lang_pack(build, lang="ca"):
    return __rows(build, [
        ('osx', 'x86_64', f'mac/x86_64/LibreOffice_{{b}}_MacOS_x86-64_langpack_{lang}.dmg', ''),
        ('osx', 'arm', f'mac/aarch64/LibreOffice_{{b}}_MacOS_aarch64_langpack_{lang}.dmg', ''),
        ('linux', 'x86_64', f'deb/x86_64/LibreOffice_{{b}}_Linux_x86-64_deb_langpack_{lang}.tar.gz', ''),
    ])


def __lang_pack_valencia(build):
    return __lang_pack(build, lang="ca-valencia")


__programs = {
    'libreoffice': __libreoffice,
    'helppack-ca': __help_pack,
    'helppack-ca-valencia': __help_pack_valencia,
    'langpack-ca': __lang_pack,
    'langpack-ca-valencia': __lang_pack_valencia,
}

add_program("libreoffice", 'libreoffice/libreoffice', 'libreoffice')
add_program("libreoffice", 'libreoffice/helppack-ca', 'paquet-dajuda-en-catala-del-libreoffice')
add_program("libreoffice", 'libreoffice/helppack-ca-valencia', 'paquet-dajuda-en-catala-valencia-del-libreoffice')
add_program("libreoffice", 'libreoffice/langpack-ca', 'paquet-catala-per-al-libreoffice')
add_program("libreoffice", 'libreoffice/langpack-ca-valencia', 'paquet-catala-valencia-per-al-libreoffice')


def __key(version):
    return tuple(int(p) for p in version.split('.'))


def highest_stable(listing):
    """Highest released version in the stable/ listing (e.g. '26.8.0')."""
    versions = re.findall(r'href="(\d+\.\d+\.\d+)/"', listing)

    return max(versions, key=__key) if versions else None


def highest_build(listing, version):
    """Highest four-part build of `version` in the archive listing
    (e.g. '26.8.0.3'); release candidates such as 26.8.0.0.beta1 are ignored."""
    builds = re.findall(r'href="(' + re.escape(version) + r'\.\d+)/"', listing)

    return max(builds, key=__key) if builds else None


def __get_latest_build():
    """(version, build): the highest version in stable/ and its highest build
    in the archive, None while the archive has no build of it yet."""
    r = requests.get(stable_url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    version = highest_stable(r.text)

    if not version:
        return None, None

    r = requests.get(archive_url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return version, highest_build(r.text, version)
