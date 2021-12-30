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
            url=f"https://inkscape.org/release/{version}/gnulinux/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/{version}/gnulinux/",
            os='linux',
        ),
        download_data(
            version,
            url=f"https://inkscape.org/release/{version}/gnulinux/",
            os='linux',
        )
    ]

