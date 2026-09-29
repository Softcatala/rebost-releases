import requests
from cachetools import TTLCache, cached

from utils import download_data, get_scoop, add_program

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/notepadplusplus.json'

add_program("notepadplusplus", 'notepadplusplus', 'notepad')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_scoop(scoop_url)

    version = d['version']

    url32 = __get_url(d, '32bit')
    url64 = __get_url(d, '64bit')

    r = []

    if url32:
        r.append(url32)

    if url64:
        r.append(url64)

    return [
        download_data(
            version=version,
            get_size=True,
            arch='x86',
            os='windows',
            url=url32
        ),
        download_data(
            version=version,
            get_size=True,
            arch='x86_64',
            os='windows',
            url=url64
        )
    ]


def __get_url(data, architecture):
    if data['architecture'] and data['architecture'][architecture] and data['architecture'][architecture]['url']:
        url = data['architecture'][architecture]['url']
        url = url.replace('.portable.', '.Installer.').replace('.zip', '.exe')
        return url
