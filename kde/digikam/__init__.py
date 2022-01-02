from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/digikam.json'

add_program("kde", 'digikam', 'digikam')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():
    d = get_scoop(scoop_url)

    version = d['version']

    return [
        download_data(
            version,
            url=f"https://www.digikam.org/download/binary/#Linux",
            os='linux',
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/digikam/{version}/digiKam-{version}-MacOS-x86-64.pkg",
            os='osx'
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/digikam/{version}/digiKam-{version}-Win64.exe",
            arch='x86_64',
            os='windows'
        )
    ]
