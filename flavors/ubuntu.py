import requests
from ubuntu_release_info import data
from ubuntu_iso_download import iso, url as uurl

from .releases import __all

flavors = {
    "desktop": uurl.Desktop,
    "server": uurl.Server,
    "netboot": uurl.Netboot,
    "budgie": uurl.Budgie,
    "kubuntu": uurl.Kubuntu,
    "kylin": uurl.Kylin,
    "lubuntu": uurl.Lubuntu,
    "ubuntu-mate": uurl.Mate,
    "studio": uurl.Studio,
    "xubuntu": uurl.Xubuntu,
}


def __other(flavor):

    if flavor not in flavors:
        return None

    f = flavors[flavor]

    for r in __all():
        if not r['dev']:
            x = __data(f, r['codename'], r['version'], __lts_version if r['lts'] else __stable_version)
            if x is not None:
                return [x]



def __desktop():
    d = data.Data()

    stable = d.stable
    lts = d.lts

    return [
        __data(uurl.Desktop, stable.codename, stable.version, __stable_version),
        __data(uurl.Desktop, lts.codename, lts.version, __lts_version)
    ]


def __stable_version(v):
    return v


def __lts_version(v):
    return f"LTS ({v})"


def __data(flavor, codename, version, v):
    try:
        i = iso.ISO(flavor, codename, "")

        hashes = requests.get(i.target.hash_file).content
        if i.verify_gpg_signature(hashes, i.target.hash_file_signed):
            filename, target_hash = i.hash()
            url = "%s/%s" % (i.target.url, filename)

            r = requests.head(url)
            size = r.headers["Content-Length"]

            return {
                'download_version': v(version),
                'download_url': url.replace('http://', 'https://'),
                'download_size': size,
                'arquitectura': 'x86_64'
            }
    except Exception as e:
        print(e)
