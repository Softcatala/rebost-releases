import re

import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, checked_rows

add_program("linuxmint", 'linuxmint', 'linux-mint')


@cached_route()
def get():
    r = requests.get('https://endoflife.date/api/linuxmint.json', timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return build(latest_release(r.json()))


def latest_release(cycles):
    """The feed also lists LMDE cycles ('lmde7'); take the newest numeric one."""
    for c in cycles:
        if re.fullmatch(r'\d+(\.\d+)*', str(c.get('cycle', ''))):
            return c['cycle']

    raise ValueError("no Linux Mint release in the feed")


def build(v):
    return checked_rows(v, [
        (f"https://mirrors.kernel.org/linuxmint/stable/{v}/linuxmint-{v}-cinnamon-64bit.iso", 'linux', 'x86_64'),
    ])
