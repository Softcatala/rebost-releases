from cachetools import cached, TTLCache

from utils import download_data, add_program, get_eol_date

add_program("debian", 'debian', 'debian')


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get():

    d = get_eol_date('debian')

    version = d['latest']

    return [
        download_data(
            'Live CD',
            url=f"https://cdimage.debian.org/debian-cd/current-live/amd64/iso-hybrid/debian-live-{version}.0-amd64-gnome.iso",
            os='linux',
            get_size=True
        ),
        download_data(
            'DVD',
            url=f"https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-{version}.0-amd64-DVD-1.iso",
            os='linux',
            get_size=True
        ),
        download_data(
            'CD',
            url=f"https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-{version}.0-amd64-netinst.iso",
            os='linux',
            get_size=True
        )
    ]
