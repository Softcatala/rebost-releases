import requests
from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

url = 'https://aus1.torproject.org/torbrowser/update_3/release/downloads.json'

add_program("tor", 'tor', 'tor')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():
    d = __get_info(url)

    version = d['version']

    return [
        download_data(
            version,
            url=d['downloads']['linux64']['ca']['binary'],
            get_size=True,
            arch="x86_64",
            os='linux',
        ),
        download_data(
            version,
            url=d['downloads']['linux32']['ca']['binary'],
            get_size=True,
            arch="x86",
            os='linux',
        ),

        download_data(
            version,
            url=d['downloads']['osx64']['ca']['binary'],
            get_size=True,
            os='osx'
        ),
        download_data(
            version,
            url=d['downloads']['win64']['ca']['binary'],
            get_size=True,
            arch="x86_64",
            os='windows'
        ),
        download_data(
            version,
            url=d['downloads']['win32']['ca']['binary'],
            get_size=True,
            arch="x86",
            os='windows'
        ),
        download_data(
            version,
            url=f"https://play.google.com/store/apps/details?id=org.torproject.torbrowser",
            arch='generic',
            os='android'
        )
    ]


def __get_info(url):
    r = requests.get(url)

    js = r.json()

    version = js['version']

    parts = version.split('.')

    js['majorVersion'] = parts[0]
    if len(parts) > 1:
        js['minorVersion'] = parts[1]
    if len(parts) > 2:
        js['patchVersion'] = parts[2]

    return js
