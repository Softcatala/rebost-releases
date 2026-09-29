import requests

from utils import REQUEST_TIMEOUT, download_data, add_program, cached_route, get_amo_addon


@cached_route()
def get(program):
    if program in __programs:
        return __programs[program]()


add_program('mozilla', 'mozilla/firefox', 'firefox')
add_program('mozilla', 'mozilla/firefox-valencia', 'firefox-en-valencia')
add_program('mozilla', 'mozilla/firefox-langpack-ca', 'paquet-catala-per-al-firefox')
add_program('mozilla', 'mozilla/firefox-langpack-ca-valencia', 'paquet-catala-valencia-per-al-firefox')
add_program('mozilla', 'mozilla/dict-ca', 'diccionari-catala-firefox')
add_program('mozilla', 'mozilla/dict-ca', 'corrector-ortografic-de-catala-general-per-a-mozilla')
add_program('mozilla', 'mozilla/dict-ca-valencia', 'diccionari-valencia-firefox')
add_program('mozilla', 'mozilla/dict-ca-valencia', 'corrector-ortografic-de-catala-valencia-per-a-mozilla')
add_program('mozilla', 'mozilla/languagetool', 'corrector-gramatical-en-catala-languagetool-per-al-firefox')
add_program('mozilla', 'mozilla/thunderbird', 'thunderbird')
add_program('mozilla', 'mozilla/thunderbird-langpack-ca', 'paquet-catala-per-al-thunderbird')
add_program('mozilla', 'mozilla/thunderbird-langpack-ca-valencia', 'paquet-catala-valencia-per-al-thunderbird')


def __firefox_catala():
    return __firefox('ca')


def __firefox_valencia():
    return __firefox('ca-valencia')


def __addon(addon_id):
    addon = get_amo_addon(addon_id)

    return [
        download_data(
            version=addon['version'],
            size=addon['size'],
            arch='generic',
            os='multiplataforma',
            url=f'https://addons.mozilla.org/firefox/downloads/latest/{addon_id}/addon-{addon_id}-latest.xpi'
        )
    ]


def __firefox_langpack_catala():
    return __addon(5019)


def __firefox_langpack_valencia():
    return __addon(9702)


def __dict_ca():
    return __addon(3369)


def __dict_ca_valencia():
    return __addon(9192)


def __thunderbird_langpack_catala():
    return __addon(5019)


def __thunderbird_langpack_valencia():
    return __addon(9702)


def __languagetool():
    addon = get_amo_addon('languagetool')

    # links to the add-on page, as the site does today
    return [
        download_data(
            version=addon['version'],
            arch='generic',
            os='multiplataforma',
            url='https://addons.mozilla.org/firefox/addon/languagetool/'
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
            url=__get_url('thunderbird', version, 'win', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86_64',
            os='windows',
            url=__get_url('thunderbird', version, 'win64', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='generic',
            os='osx',
            url=__get_url('thunderbird', version, 'osx', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux',
            url=__get_url('thunderbird', version, 'linux', 'ca')
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='linux_64',
            url=__get_url('thunderbird', version, 'linux64', 'ca')
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
    'languagetool': __languagetool,
    'thunderbird': __thunderbird,
    'thunderbird-langpack-ca': __thunderbird_langpack_catala,
    'thunderbird-langpack-ca-valencia': __thunderbird_langpack_valencia,
}


def __get_url(product, version, moz_os, lang):
    return f'https://download.mozilla.org/?product={product}-{version}-SSL&os={moz_os}&lang={lang}'


def __get_version(url, key):
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return r.json()[key]
