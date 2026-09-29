import re
from urllib.parse import quote
from xml.etree import ElementTree

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, check_urls, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/omegat.json'
folder = '/OmegaT - Standard/OmegaT {v}'
media = '{http://video.search.yahoo.com/mrss/}content'

add_program("omegat", 'omegat', 'omegat')

# (pattern for the file name, os, arch, required); the folder listing is the
# only place where the exact names are known
files = [
    (r'^OmegaT_{v}_Windows_64_signed\.exe$', 'windows', 'x86_64', True),
    (r'^OmegaT_{v}_Windows_aarch64_signed\.exe$', 'windows', 'arm', False),
    (r'^OmegaT_{v}_Mac.*\.zip$', 'osx', 'generic', False),
    (r'^OmegaT_{v}_Linux_64\.tar\.bz2$', 'linux', 'x86_64', True),
    (r'^OmegaT_{v}_Without_JRE\.zip$', 'multiplataforma', 'generic', True),
]


@cached_route()
def get():
    v = get_scoop(scoop_url)['version']

    r = requests.get('https://sourceforge.net/projects/omegat/rss',
                     params={'path': folder.format(v=v)}, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return build(v, r.text)


def parse_listing(rss):
    """{file name: url} from the SourceForge folder feed"""
    found = {}
    for item in ElementTree.fromstring(rss).iter(media):
        url = item.get('url')
        found[url.rsplit('/', 2)[-2].replace('%20', ' ')] = url

    return found


def build(v, rss):
    listing = parse_listing(rss)

    picked = []
    for pattern, os, arch, required in files:
        regex = re.compile(pattern.replace('{v}', re.escape(v)), re.I)
        names = [n for n in listing if regex.search(n)]
        if len(names) == 1:
            picked.append((listing[names[0]], os, arch))
        elif required or names:
            raise ValueError(f"{pattern!r} matched {names} for OmegaT {v}")

    sizes = check_urls([p[0] for p in picked])

    return [download_data(v, url=url, size=sizes[url], arch=arch, os=os) for url, os, arch in picked]
