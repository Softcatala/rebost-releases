import requests
from cachetools import cached, TTLCache

from utils import download_data, add_program

add_program("fedora", 'fedora', 'fedora')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_fedora()

    version = d['version']

    return [
        download_data(
            version,
            url=d['link'],
            os='linux',
            get_size=True
        )
    ]

def get_fedora():
    url = 'https://fedoraproject.org/releases.json'

    r = requests.get(url)

    js = r.json()

    stable = False

    stable = list(filter(lambda x: 'Beta' not in x['version'], js))
    stable = list(filter(lambda x: x['arch'] == 'x86_64' and x['variant']=='Workstation', stable))

    if len(stable) > 0:
        return stable[0]
