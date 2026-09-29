import requests
from cachetools import cached, TTLCache

from utils import download_data, add_program

url = 'https://aus1.torproject.org/torbrowser/update_3/release/downloads.json'

add_program("tor", 'tor', 'navegador-tor')

# (key in the feed, os, arch)
__platforms = [
    ('linux-x86_64', 'linux', 'x86_64'),
    ('linux-i686', 'linux', 'x86'),
    ('macos', 'osx', 'generic'),
    ('win64', 'windows', 'x86_64'),
    ('win32', 'windows', 'x86'),
]


def get():
    try:
        return __cached_get()
    except Exception as e:
        print(f"tor: {e!r}")

    return None


# Failures raise, so that they are not kept in the cache
@cached(cache=TTLCache(maxsize=10, ttl=300))
def __cached_get():
    r = requests.get(url)
    r.raise_for_status()

    rows = parse(r.json())

    if not rows:
        raise ValueError("no desktop downloads found in the feed")

    return rows


def parse(d):
    """Builds the rows from the downloads.json feed; a platform missing from
    the feed only removes its own row."""
    version = d['version']
    downloads = d.get('downloads', {})

    rows = []
    for key, os, arch in __platforms:
        try:
            binary = downloads[key]['ALL']['binary']
        except (KeyError, TypeError):
            print(f"tor: no download for '{key}'")
            continue

        rows.append(download_data(version, url=binary, get_size=True, arch=arch, os=os))

    if not rows:
        return None

    rows.append(download_data(
        version,
        url="https://play.google.com/store/apps/details?id=org.torproject.torbrowser",
        arch='generic',
        os='android'
    ))

    return rows
