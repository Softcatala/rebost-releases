import re

import requests
from cachetools import cached, TTLCache

from utils import add_program, download_data

stable_url = 'https://download.documentfoundation.org/libreoffice/stable/'
archive_url = 'https://downloadarchive.documentfoundation.org/libreoffice/old/'


def get(program):
    if program not in __programs:
        return None

    try:
        return __cached_get(program)
    except Exception as e:
        print(f"libreoffice/{program}: {e!r}")

    return None


# Failures raise, so that they are not kept in the cache
@cached(cache=TTLCache(maxsize=10, ttl=300))
def __cached_get(program):
    build = __get_latest_build()

    if not build:
        raise ValueError("could not find the latest LibreOffice version")

    return __programs[program](build)


def __rows(build, entries):
    """entries: (os, arch, path, version label suffix)"""
    version = '.'.join(build.split('.')[:3])

    return [
        download_data(
            version=f"{version}{label}",
            get_size=True,
            os=os,
            arch=arch,
            url=f"{archive_url}{build}/{path.format(b=build)}"
        )
        for os, arch, path, label in entries
    ]


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
    r = requests.get(stable_url)
    r.raise_for_status()
    version = highest_stable(r.text)

    if not version:
        return None

    r = requests.get(archive_url)
    r.raise_for_status()

    return highest_build(r.text, version)
