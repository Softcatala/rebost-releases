from cachetools import cached, TTLCache

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/gimp.json'

add_program("gimp", 'gimp', 'gimp')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_scoop(scoop_url)

    version = d['version']
    major_version = d['majorVersion']
    minor_version = d['minorVersion']

    if "-" in version:
        winversion = version.replace('-', '-setup-')
        macversion = f"{version.split('-')[0]}-x86_64"

    else:
        winversion = f"{version}-setup"
        macversion = f"{version}-x86_64"


    return [
        download_data(
            version,
            url="https://www.gimp.org/downloads/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://download.gimp.org/mirror/pub/gimp/v{major_version}.{minor_version}/osx/gimp-{macversion}.dmg",
            os='osx',
            get_size=True
        ),
        download_data(
            version,
            url=f"https://download.gimp.org/mirror/pub/gimp/v{major_version}.{minor_version}/windows/gimp-{winversion}.exe",
            arch='x86_64',
            os='windows',
            get_size=True
        )
    ]
