from utils import download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/inkscape.json'


def get():

    d = get_scoop(scoop_url)

    version = d['version']

    return [
        download_data(
            version,
            url=f"https://inkscape.org/release/{version}/gnulinux/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/mac-os-x/dmg/dl/",
            os='osx'
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/windows/64-bit/exe/dl/",
            arch='x86_64',
            os='windows'
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/inkscape-{version}/windows/32-bit/exe/dl/",
            arch='x86',
            os='windows'
        )
    ]
