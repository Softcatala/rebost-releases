import re

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, download_data

version_url = 'https://version.qgis.org/version.txt'
landing = 'https://qgis.org/download/'

add_program("qgis", 'qgis', 'qgis')


@cached_route()
def get():
    r = requests.get(version_url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return build(parse_version(r.text))


def parse_version(text):
    """The first line is '#QGIS Version 40202|...' and the body says 'The
    current released version of QGIS is 4.2.2.'"""
    m = re.search(r'current released version of QGIS is (\d+\.\d+\.\d+)', text)
    if m:
        return m.group(1)

    m = re.match(r'#QGIS Version (\d)(\d\d)(\d\d)', text)
    if m:
        return '.'.join(str(int(g)) for g in m.groups())

    raise ValueError("unexpected QGIS version.txt")


def build(v):
    # installer names are not predictable, so every row is a landing page
    return [download_data(v, url=landing, arch='generic', os=os) for os in ('windows', 'osx', 'linux')]
