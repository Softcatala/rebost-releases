from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/krita.json'

add_program("kde", 'krita', 'krita')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_scoop(scoop_url)

    version = d['version']

    return [
        download_data(
            version,
            url=f"appstream://org.kde.krita",
            os='linux',
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/krita/{version}/krita-{version}.dmg",
            os='osx'
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/krita/{version}/krita-x64-{version}-setup.exe",
            arch='x86_64',
            os='windows'
        )
    ]
