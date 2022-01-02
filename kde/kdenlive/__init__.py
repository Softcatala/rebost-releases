from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/kdenlive.json'

add_program("kde", 'kdenlive', 'kdenlive')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_scoop(scoop_url)

    version = d['version']

    return [
        download_data(
            version,
            url=f"https://kdenlive.org/en/download2/",
            os='linux',
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/kdenlive/{d['majorVersion']}.{d['minorVersion']}/macOS/kdenlive-{version}.dmg",
            os='osx'
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://download.kde.org/stable/kdenlive/{d['majorVersion']}.{d['minorVersion']}/windows/kdenlive-{version}.exe",
            os='windows'
        )
    ]
