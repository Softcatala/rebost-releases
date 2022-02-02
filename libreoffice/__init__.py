from cachetools import cached, TTLCache

from utils import add_program, get_scoop, download_data

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/libreoffice.json'


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(program):
    pass
    # if program in __programs:
    #    return __programs[program]()


def __libreoffice():

    d = get_scoop(scoop_url)

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
    d = get_scoop(scoop_url)

    return [
        download_data(
            version=f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}",
            get_size=True,
            os='windows',
            arch='x86',
            url=__get_download_url(d['version'], 'win', 'x86', f"{d['majorVersion']}.{d['minorVersion']}.{d['patchVersion']}" f"{package}_{lang}")
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
    d = get_scoop(scoop_url)

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
        'x86_64': '_x64'
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
    base = 'https://downloadarchive.documentfoundation.org/libreoffice/old'

    package = f'_{package}' if package != "" else ""

    return f'{base}/{version}/{os}/{arch}/LibreOffice_{shortversion}{__platform_suffix[os]}{__arch_suffix[os][arch]}{package}.{__extension[os]}'
