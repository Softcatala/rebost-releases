import re
from concurrent.futures import ThreadPoolExecutor

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, download_data, check_urls

redirector = 'https://www.zotero.org/download/client/dl?channel=release&platform={}'

# (platform, os, arch)
platforms = [
    ('win-x64', 'windows', 'x86_64'),
    ('mac', 'osx', 'generic'),
    ('linux-x86_64', 'linux', 'x86_64'),
]

add_program("zotero", 'zotero', 'zotero')


def locate(platform):
    r = requests.get(redirector.format(platform), allow_redirects=False, timeout=REQUEST_TIMEOUT)

    return r.headers.get('Location', '')


@cached_route()
def get():
    with ThreadPoolExecutor(max_workers=len(platforms)) as pool:
        locations = list(pool.map(lambda p: locate(p[0]), platforms))

    return build(locations)


def parse_location(location):
    """https://download.zotero.org/client/release/10.0.3/Zotero-10.0.3_x64_setup.exe"""
    m = re.search(r'/client/release/(\d+(?:\.\d+)+)/', location)
    if not m:
        raise ValueError(f"unexpected Zotero location {location!r}")

    return m.group(1)


def build(locations):
    # platforms can be on different patch versions on the same day
    sizes = check_urls(locations)

    return [
        download_data(parse_location(location), url=location, size=sizes[location], arch=arch, os=os)
        for location, (_, os, arch) in zip(locations, platforms)
    ]
