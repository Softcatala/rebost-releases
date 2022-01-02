import requests
from cachetools import TTLCache, cached

from utils import download_data, add_program


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(program):
    if program in __programs:
        return __programs[program]()


add_program('mozilla', 'firefox', 'firefox')
add_program('mozilla', 'firefox-valencia', 'firefox-en-valencia')
add_program('mozilla', 'firefox-langpack-ca', 'paquet-catala-per-al-firefox')
add_program('mozilla', 'firefox-langpack-ca-valencia', 'paquet-catala-valencia-per-al-firefox')
add_program('mozilla', 'dict-ca', 'diccionari-catala-firefox')
add_program('mozilla', 'dict-ca-valencia', 'diccionari-valencia-firefox')
add_program('mozilla', 'thunderbird', 'thunderbird')
add_program('mozilla', 'thunderbird-langpack-ca', 'paquet-catala-per-al-thunderbird')
add_program('mozilla', 'thunderbird-langpack-ca-valencia', 'paquet-catala-valencia-per-al-thunderbird')


def __firefox_catala():
    return __firefox('ca')


def __firefox_valencia():
    return __firefox('ca-valencia')


def __firefox_langpack_catala():
    return [
        download_data(
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/5019/addon-5019-latest.xpi'
        )
    ]


def __firefox_langpack_valencia():
    return [
        download_data(
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/9702/addon-9702-latest.xpi'
        )
    ]


def __dict_ca():
    return [
        download_data(
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/3369/addon-3369-latest.xpi'
        )
    ]


def __dict_ca_valencia():
    return [
        download_data(
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/9192/addon-9192-latest.xpi'
        )
    ]


def __thunderbird_langpack_catala():
    return [
        download_data(
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/5019/addon-5019-latest.xpi'
        )
    ]


def __thunderbird_langpack_valencia():
    return [
        download_data(
            version='',
            get_size=True,
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/downloads/latest/9702/addon-9702-latest.xpi'
        )
    ]


def __thunderbird():
    version = __get_version(_thunderbird_url, 'LATEST_THUNDERBIRD_VERSION')

    return [
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='windows',
            url=__get_url('firefox', version, 'win', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86_64',
            os='windows',
            url=__get_url('firefox', version, 'win64', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='generic',
            os='osx',
            url=__get_url('firefox', version, 'osx', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux',
            url=__get_url('firefox', version, 'linux', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux_64',
            url=__get_url('firefox', version, 'linux64', 'ca')
        ),
    ]


_firefox_url = 'https://product-details.mozilla.org/1.0/firefox_versions.json'
_thunderbird_url = 'https://product-details.mozilla.org/1.0/thunderbird_versions.json'


def __firefox(lang):
    version = __get_version(_firefox_url, 'LATEST_FIREFOX_VERSION')

    return [
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='windows',
            url=__get_url('firefox', version, 'win', lang)
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86_64',
            os='windows',
            url=__get_url('firefox', version, 'win64', lang)
        ),
        download_data(
            version=version,
            get_size=True,
            arch='generic',
            os='osx',
            url=__get_url('firefox', version, 'osx', lang)
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux',
            url=__get_url('firefox', version, 'linux', lang)
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux_64',
            url=__get_url('firefox', version, 'linux64', lang)
        ),
        download_data(
            version=version,
            arch='generic',
            os='android',
            url='https://play.google.com/store/apps/details?id=org.mozilla.firefox'
        ),
        download_data(
            version=version,
            arch='generic',
            os='ios',
            url='https://itunes.apple.com/app/apple-store/id989804926'
        ),
    ]


__programs = {
    'firefox': __firefox_catala,
    'firefox-valencia': __firefox_valencia,
    'firefox-langpack-ca': __firefox_langpack_catala,
    'firefox-langpack-ca-valencia': __firefox_langpack_valencia,
    'dict-ca': __dict_ca,
    'dict-ca-valencia': __dict_ca_valencia,
    'thunderbird': __thunderbird,
    'thunderbird-langpack-valencia': __thunderbird_langpack_catala,
    'thunderbird-langpack-ca-valencia': __thunderbird_langpack_valencia,
}


def __get_url(product, version, moz_os, lang):
    return f'https://download.mozilla.org/?product={product}-{version}-SSL&os={moz_os}&lang={lang}'


def __get_version(url, key):
    r = requests.get(url)

    js = r.json()

    return js[key]
