import requests, re

from cachetools import cached, TTLCache

from utils import add_program, download_data

@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(program):
    if program in __programs:
       return __programs[program]()


def __libreoffice():
    d = __get_latest_version()

    return [
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='windows',
            arch='x86',
            url=__get_download_url(d['version'], 'win', 'x86', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='windows',
            arch='x86_64',
            url=__get_download_url(d['version'], 'win', 'x86_64', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='osx',
            arch='x86_64',
            url=__get_download_url(d['version'], 'mac', 'x86_64', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            os='linux',
            arch='generic',
            url="https://www.libreoffice.org/download/download/?type=deb-x86_64&lang=ca"
        )
    ]


def __help_pack(package="helppack", lang="ca"):
    d = __get_latest_version()


    return [
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='windows',
            arch='x86',
            url=__get_download_url(d['version'], 'win', 'x86', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}", f"{package}_{lang}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='windows',
            arch='x86_64',
            url=__get_download_url(d['version'], 'win', 'x86_64', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}", f"{package}_{lang}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            os='linux',
            arch='generic',
            url=f"https://www.libreoffice.org/download/download/?type=deb-x86_64&lang={lang}"
        )
    ]


def __help_pack_valencia():
    return __help_pack(lang="ca-valencia")


def __lang_pack(package="langpack", lang="ca"):
    d = __get_latest_version()

    return [
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='osx',
            arch='x86_64',
            url=__get_download_url(d['version'], 'mac', 'x86_64', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}", f"{package}_{lang}")
        ),
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            os='linux',
            arch='generic',
            url=f"https://www.libreoffice.org/download/download/?type=deb-x86_64&lang={lang}"
        )
    ]


def __lang_pack_valencia():
    return __lang_pack(lang="ca-valencia")


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


__arch_suffix = {
    'win' : {
        'x86': '_x86',
        'x86_64': '_x86-64'
    },
    'mac' : {
        'x86': '_x86',
        'x86_64': '_x86-64'
    }
}

__platform_suffix = {
    'win': '_Win',
    'mac': '_MacOS'
}

__extension = {
    'win': 'msi',
    'mac': 'dmg'
}


def __get_download_url(version, os, arch, shortversion, package=""):
    base = 'https://downloadarchive.documentfoundation.org/libreoffice/old/'

    package = f'_{package}' if package != "" else ""

    return f'{base}/{version}/{os}/{arch}/LibreOffice_{version}{__platform_suffix[os]}{__arch_suffix[os][arch]}{package}.{__extension[os]}'


def __get_latest_version():
    url = 'https://downloadarchive.documentfoundation.org/libreoffice/old/latest/win/x86/'

    r = requests.get(url)

    body = r.text

    exp = re.search('href="LibreOffice_([\d\.]+)_Win_x86.msi"', body)

    if exp:
        g = exp.groups()

        if g:
            version = g[0]

            parts = version.split('.')

            js = {}
            js['version'] = version
            js['majorVersion'] = parts[0]
            if len(parts) > 1:
                js['minorVersion'] = parts[1]
            if len(parts) > 2:
                js['patchVersion'] = parts[2]

            return js
