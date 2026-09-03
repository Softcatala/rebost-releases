from cachetools import cached, TTLCache

from ubuntu import iso, releases
from utils import download_data, add_program

add_program("ubuntu", 'ubuntu/ubuntu', 'ubuntu')
add_program("ubuntu", 'ubuntu/xubuntu', 'xubuntu')
add_program("ubuntu", 'ubuntu/kubuntu', 'kubuntu')
add_program("ubuntu", 'ubuntu/ubuntu-mate', 'ubuntu-mate')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(flavor):
    try:
        if flavor == 'ubuntu':
            return __desktop()
        else:
            return __other(flavor)
    except Exception as e:
        print(e)

    return None


def __desktop():
    stable = releases.stable()
    lts = releases.lts()

    found = [__data('desktop', stable)]

    # the newest supported release is often the LTS itself, and there is no
    # point in offering the very same download twice
    if lts and lts['codename'] != stable['codename']:
        found.append(__data('desktop', lts))

    return [f for f in found if f is not None]


def __other(flavor):
    if flavor not in iso.flavors:
        return None

    # a flavor does not publish an image for every release, so walk the
    # supported ones from the newest down until one of them has an ISO
    for r in releases.supported():
        if not r['dev']:
            d = __data(flavor, r)

            if d is not None:
                return [d]


def __data(flavor, release):
    if release is None:
        return None

    try:
        found = iso.get(flavor, release)
    except Exception as e:
        # a flavor that has not published this release yet just 404s, and the
        # caller is expected to fall back to an older one
        print(e)
        return None

    if found is None:
        return None

    print(f"Got {flavor} {release['codename']} at {found['url']}")

    return download_data(
        version=__version(found['version'], release['lts']),
        url=found['url'],
        size=found['size'],
        arch='x86_64',
        os='linux'
    )


def __version(version, lts):
    return f"LTS ({version})" if lts else version
