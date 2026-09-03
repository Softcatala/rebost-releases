"""Locate the current ISO for Ubuntu and each of its flavors.

Ubuntu Desktop and Server publish simplestreams metadata on releases.ubuntu.com
that already carries the filename, the size and the checksum of every image, so
a single request is enough. The flavors only publish a SHA256SUMS file on
cdimage.ubuntu.com, so their filename has to be read out of there and the size
asked for separately.

This covers the part of the archived ubuntu-iso-download package this app used.
"""

import re

import requests

from utils import get_content_size

ARCHIVE = "https://archive.ubuntu.com"
CDIMAGE = "https://cdimage.ubuntu.com"
RELEASES = "https://releases.ubuntu.com"

STREAMS = RELEASES + "/streams/v1/com.ubuntu.releases:%s.json"

ARCH = "amd64"

# Desktop and Server come from simplestreams, keyed by the product name and the
# image types to accept: Server was plain "server" until 18.04 and "live-server"
# from then on, and the "ubuntu" product also carries WSL images we don't want.
# Everything else is a cdimage flavor, keyed by its directory and its ISO
# variety, which is "desktop" for all of them but Studio.
flavors = {
    "desktop": {'stream': 'ubuntu', 'types': ('desktop',)},
    "server": {'stream': 'ubuntu-server', 'types': ('live-server', 'server')},
    "budgie": {'cdimage': 'ubuntu-budgie'},
    "kubuntu": {'cdimage': 'kubuntu'},
    "kylin": {'cdimage': 'ubuntukylin'},
    "lubuntu": {'cdimage': 'lubuntu'},
    "ubuntu-mate": {'cdimage': 'ubuntu-mate'},
    "studio": {'cdimage': 'ubuntustudio', 'variety': 'dvd'},
    "xubuntu": {'cdimage': 'xubuntu'},
    "netboot": {'netboot': True},
}


def get(flavor, release):
    """Return the ISO published for a flavor and release, or None.

    A flavor does not necessarily publish an image for every release, and it
    can lag behind the archive by a point release, so the version reported is
    the one of the image actually found rather than the one of the release.

    Args:
        flavor: key of the flavors dict (e.g. desktop, kubuntu)
        release: release dict as returned by ubuntu.releases

    Returns:
        dict with version, url and size, or None when there is no such image

    """
    if flavor not in flavors:
        return None

    f = flavors[flavor]

    if 'stream' in f:
        return __from_stream(f['stream'], f['types'], release)

    if 'netboot' in f:
        return __from_netboot(release)

    return __from_cdimage(f['cdimage'], f.get('variety', 'desktop'), release)


def __from_stream(product, types, release):
    """Read the ISO out of the simplestreams metadata on releases.ubuntu.com."""
    r = requests.get(STREAMS % product)
    r.raise_for_status()

    found = None

    for p in r.json()['products'].values():
        if (p['release'] != release['codename']
                or p['arch'] != ARCH
                or p['image_type'] not in types):
            continue

        # a product holds every point release, so keep the newest one
        for version, data in p['versions'].items():
            iso = data['items'].get('iso')

            if iso and (found is None or compare(version) > found[0]):
                found = (compare(version), version, iso)

    if found is None:
        return None

    _, version, iso = found

    return {
        'version': version,
        'url': "%s/%s" % (RELEASES, iso['path']),
        'size': iso['size']
    }


def __from_cdimage(flavor, variety, release):
    """Pick the ISO out of the SHA256SUMS a flavor publishes on cdimage."""
    base = "%s/%s/releases/%s/release" % (CDIMAGE, flavor, release['codename'])

    # e.g. kubuntu-24.04.4-desktop-amd64.iso, ubuntustudio-24.04.4-dvd-amd64.iso
    pattern = re.compile(r"^%s-(.+?)-%s-%s\.iso$" % (
        re.escape(flavor), re.escape(variety), ARCH
    ))

    found = newest(__hashed_files("%s/SHA256SUMS" % base), pattern)

    if found is None:
        return None

    version, name = found
    url = "%s/%s" % (base, name)

    return {'version': version, 'url': url, 'size': __size(url)}


def __from_netboot(release):
    """Find the mini.iso, which lives in the archive and was dropped after 19.10."""
    if release['compare'] >= 2004:
        return None

    base = "%s/ubuntu/dists/%s/main/installer-%s/current/images" % (
        ARCHIVE, release['codename'], ARCH
    )

    for name in __hashed_files("%s/SHA256SUMS" % base):
        if name.endswith('mini.iso'):
            url = "%s/%s" % (base, name.lstrip('./'))

            return {
                'version': release['version'],
                'url': url,
                'size': __size(url)
            }


def newest(names, pattern):
    """Return the (version, name) of the newest filename matching a pattern.

    A release directory holds every point release of a flavor, so the version
    captured by the pattern is what decides which one is current. The order the
    names come in is not relied on.
    """
    found = None

    for name in names:
        m = pattern.match(name)

        if m and (found is None or compare(m.group(1)) > found[0]):
            found = (compare(m.group(1)), m.group(1), name)

    return (found[1], found[2]) if found else None


def __hashed_files(hash_file):
    """Yield the filenames listed in a SHA256SUMS file."""
    r = requests.get(hash_file)
    r.raise_for_status()

    for line in r.content.decode('utf-8').splitlines():
        # entries are "<sha256> *<filename>" or "<sha256>  <filename>"
        parts = line.split(' ')

        if len(parts) > 1:
            yield parts[-1].lstrip('*')


def compare(version):
    """Return a sortable key for a version such as 24.04.4."""
    return tuple(int(p) if p.isdigit() else 0 for p in version.split('.'))


def __size(url):
    try:
        return get_content_size(url)
    except Exception:
        return ""
