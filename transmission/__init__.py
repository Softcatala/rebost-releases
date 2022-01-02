from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/transmission.json'

add_program("transmission", 'transmission', 'transmission')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():
    d = get_scoop(scoop_url)

    version = d['version']

    return [
        download_data(
            version,
            url=f"https://transmissionbt.com/download/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://github.com/transmission/transmission-releases/raw/master/Transmission-{version}.dmg",
            os='osx'
        ),
        download_data(
            version,
            url=f"https://github.com/transmission/transmission-releases/raw/master/transmission-{version}-x64.msi",
            arch='x86_64',
            os='windows'
        ),
        download_data(
            version,
            url=f"https://github.com/transmission/transmission-releases/raw/master/transmission-{version}-x86.msi",
            arch='x86',
            os='windows'
        )
    ]
