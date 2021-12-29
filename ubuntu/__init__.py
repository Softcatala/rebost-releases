import requests
from cachetools import cached, TTLCache
from ubuntu_release_info import data
from ubuntu_iso_download import iso, url as uurl

from ubuntu.releases import __all
from utils import download_data


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(flavor):
    try:
        if flavor == 'ubuntu':
            return __desktop()
        else:
            return __other(flavor)
    except:
        pass

    return None


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
            print(f"Getting {codename} {version}")
            filename, target_hash = i.hash()
            url = "%s/%s" % (i.target.url, filename)
            print(f"Url {url}")
            r = requests.head(url)
            size = r.headers["Content-Length"]

            return download_data(
                version=v(version),
                url=url.replace('http://', 'https://'),
                size=size,
                arch='x86_64',
                os='multiplataforma'
            )
    except Exception as e:
        print(e)
