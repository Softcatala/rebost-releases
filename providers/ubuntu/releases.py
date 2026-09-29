"""Ubuntu release metadata, read straight from changelogs.ubuntu.com.

The meta-release file lists every Ubuntu ever released, each with a Supported
flag; meta-release-development additionally carries the release currently
under development. Between them they give the same information the archived
ubuntu-release-info package used to provide.
"""

import requests
from cachetools import cached, TTLCache

META_RELEASE = "https://changelogs.ubuntu.com/meta-release"
META_RELEASE_DEV = "https://changelogs.ubuntu.com/meta-release-development"


@cached(cache=TTLCache(maxsize=1, ttl=3600))
def supported():
    """Return the currently supported releases, newest first."""
    releases = {r['codename']: r for r in __fetch(META_RELEASE)}

    # whatever only shows up in the development file is the release being
    # worked on: it has no Supported flag yet, but we still want it listed
    for r in __fetch(META_RELEASE_DEV):
        if r['codename'] not in releases:
            r['dev'] = True
            r['supported'] = True
            releases[r['codename']] = r

    found = [r for r in releases.values() if r['supported']]

    return sorted(found, key=lambda r: r['compare'], reverse=True)


def stable():
    """Return the newest supported release that is not the development one."""
    return next((r for r in supported() if not r['dev']), None)


def lts():
    """Return the newest supported LTS release."""
    return next((r for r in supported() if r['lts'] and not r['dev']), None)


def parse(text):
    """Yield a release for every record in a meta-release file.

    Records are blank line separated blocks of "Key: value" lines; blocks
    without a Dist key are blank lines at the end of the file.
    """
    for block in text.split('\n\n'):
        fields = dict(l.split(': ', 1) for l in block.splitlines() if ': ' in l)

        if 'Dist' in fields:
            yield __info(fields)


def __fetch(url):
    r = requests.get(url)
    r.raise_for_status()

    return parse(r.content.decode('utf-8'))


def __info(fields):
    version = fields['Version'].replace(' LTS', '')
    year, month = (int(p) for p in version.split('.')[:2])

    return {
        'codename': fields['Dist'],
        'version': version,
        'compare': year * 100 + month,
        'lts': 'LTS' in fields['Version'],
        'dev': False,
        'supported': fields['Supported'] == '1'
    }
