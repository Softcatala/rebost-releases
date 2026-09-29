import re

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, checked_rows, download_data

base = 'https://updates.signal.org/desktop'

add_program("signal", 'signal', 'signal-private-messenger')


@cached_route()
def get():
    return build(fetch('latest.yml'), fetch('latest-mac.yml'))


def fetch(name):
    r = requests.get(f'{base}/{name}', timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.text


def parse(text):
    """Reads the version and the file names of an electron-builder feed;
    a regular expression is enough for these two fields."""
    m = re.search(r'^version:\s*(\S+)', text, re.M)
    if not m:
        raise ValueError("no version in the Signal feed")

    return m.group(1), re.findall(r'^\s*-\s*url:\s*(\S+)', text, re.M)


def build(win_yml, mac_yml):
    version, win_files = parse(win_yml)
    mac_version, mac_files = parse(mac_yml)

    exe = f'signal-desktop-win-x64-{version}.exe'
    # the mac feed also lists .zip update packages; the installer is the dmg
    dmg = [f for f in mac_files if f.endswith('.dmg')]

    if exe not in win_files or len(dmg) != 1:
        raise ValueError(f"unexpected Signal files: {win_files} {mac_files}")

    rows = checked_rows(version, [
        (f'{base}/{exe}', 'windows', 'x86_64'),
        (f'{base}/{dmg[0]}', 'osx', 'generic'),
    ])
    rows += [
        download_data(version, arch='generic', os='android',
                      url='https://play.google.com/store/apps/details?id=org.thoughtcrime.securesms'),
        download_data(version, arch='generic', os='ios',
                      url='https://apps.apple.com/us/app/signal-private-messenger/id874139669'),
    ]

    return rows
