import re

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, checked_rows, download_data

base = 'https://download.virtualbox.org/virtualbox'

add_program("virtualbox", 'virtualbox', 'virtualbox')


@cached_route()
def get():
    r = requests.get(f'{base}/LATEST-STABLE.TXT', timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    version = parse_version(r.text)

    r = requests.get(f'{base}/{version}/SHA256SUMS', timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return build(version, r.text)


def parse_version(text):
    version = text.strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError(f"unexpected LATEST-STABLE.TXT: {text[:40]!r}")

    return version


def find_file(sums, version, suffix):
    """File names carry a build number: VirtualBox-7.2.20-175154-Win.exe"""
    # each line is "<hash> *<file>"
    m = re.search(rf'\*(VirtualBox-{re.escape(version)}-\d+-{suffix})\s*$', sums, re.M)
    if not m:
        raise ValueError(f"no {suffix} file for VirtualBox {version}")

    return m.group(1)


def build(version, sums):
    url = lambda suffix: f"{base}/{version}/{find_file(sums, version, suffix)}"

    rows = checked_rows(version, [
        (url(r'Win\.exe'), 'windows', 'x86_64'),
        (url(r'OSX\.dmg'), 'osx', 'x86_64'),
        (url(r'macOSArm64\.dmg'), 'osx', 'arm'),
    ])
    rows.append(download_data(version, url='https://www.virtualbox.org/wiki/Linux_Downloads',
                              arch='generic', os='linux'))

    return rows
