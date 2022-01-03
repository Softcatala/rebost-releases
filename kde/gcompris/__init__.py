import json

from cachetools import cached, TTLCache

from utils import download_data, add_program, get_gitlab_tag_rss

gitlab_tags_rss = 'https://invent.kde.org/education/gcompris/-/tags?format=atom'

add_program("kde", 'gcompris', 'gcompris')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_gitlab_tag_rss(gitlab_tags_rss, 'V')

    version = d['version']

    return [
        download_data(
            version,
            url=f"https://gcompris.net/downloads-ca.html#linux",
            os='linux',
        ),
        download_data(
            version,
            get_size=True,
            url=f"https://gcompris.net/download/qt/macos/gcompris-qt-{version}-Darwin.dmg",
            os='osx'
        ),
        download_data(
            version,
            get_size=True,
            arch='x86_64',
            url=f"https://gcompris.net/download/qt/windows/gcompris-qt-{version}-win64-gcc.exe",
            os='windows'
        ),
        download_data(
            version,
            get_size=True,
            arch='x86',
            url=f"https://gcompris.net/download/qt/windows/gcompris-qt-{version}-win32-gcc.exe",
            os='windows'
        ),
        download_data(
            version,
            url=f"https://play.google.com/store/apps/details?id=net.gcompris.full",
            arch='generic',
            os='android'
        )
    ]
