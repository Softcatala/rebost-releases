from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/inkscape.json'

add_program("inkscape", 'inkscape', 'inkscape')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_scoop(scoop_url)

    version = d['version'].split('_')[0]

    return [
        download_data(
            version,
            url=f"https://inkscape.org/release/{version}/gnulinux/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/mac-os-x/dmg/dl/",
            os='osx'
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/mac-os-x/dmg/dl/",
            os='osx',
            arch='arm'
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/windows/64-bit/exe/dl/",
            arch='x86_64',
            os='windows'
        )
    ]
