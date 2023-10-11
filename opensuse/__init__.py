from cachetools import cached, TTLCache

from utils import download_data, add_program, get_eol_date

add_program("opensuse", 'opensuse', 'opensuse')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_eol_date('opensuse')

    version = d['cycle']

    return [
        download_data(
            version,
            url=f"https://download.opensuse.org/distribution/leap/{version}/iso/openSUSE-Leap-{version}-DVD-x86_64-Media.iso",
            os='linux',
            get_size=True
        ),
        download_data(
            'Tumbleweed',
            url=f"https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-DVD-x86_64-Current.iso",
            os='linux',
            get_size=True
        )
    ]
