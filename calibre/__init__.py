from cachetools import TTLCache, cached

from utils import download_data, add_program
import feedparser

add_program("calibre", 'calibre', 'calibre')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    feed = feedparser.parse("https://calibre-ebook.com/changelog.rss")

    parts = feed.entries[0].id.split('-')
    version=parts[1]

    return [
        download_data(
            version,
            url="https://calibre-ebook.com/download_linux",
            os='linux',
        ),
        download_data(
            version,
            url="https://calibre-ebook.com/dist/osx",
            os='osx'
        ),
        download_data(
            version,
            url="https://calibre-ebook.com/dist/win64",
            arch='x86_64',
            os='windows'
        ),
        download_data(
            version,
            url="https://calibre-ebook.com/dist/win32",
            arch='x86_64',
            os='windows'
        ),
        download_data(
            version=f"{version} (portable)",
            url="https://calibre-ebook.com/download_portable",
            os='windows'
        )
    ]