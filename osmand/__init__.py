import re

import requests
from cachetools import cached, TTLCache

from utils import download_data, add_program

__base_url = 'https://gent.softcatala.org/albert/mapa/'

add_program("osmand", 'osmand', 'mapa-catala-per-a-losmand')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():
    r = requests.get(__base_url)

    downloads = __extract_info(r.text)

    return [download_data(
        version=d['version'],
        url=d['url'],
        human_size=d['size']
    ) for d in downloads]


def __extract_info(text):
    links_regexp = re.compile("href='' class='name'>(.*).obf<")
    size_regexp = re.compile(">([^<]* MB)<")

    link_match = links_regexp.findall(text)
    size_match = size_regexp.findall(text)

    if not link_match or not size_match:
        return

    info = []
    for idx, _ in enumerate(link_match):
        info.append({
            'url':  f"{__base_url}{link_match[idx]}.obf",
            'version': link_match[idx].replace('Territori-catala-', ''),
            'size': size_match[idx]
        })

    return sorted(info, key=lambda x: x['version'], reverse=True)
