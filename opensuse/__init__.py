from utils import add_program, cached_route, check_urls, download_data, get_eol_date

add_program("opensuse", 'opensuse', 'opensuse')


@cached_route()
def get():
    return build(get_eol_date('opensuse')['cycle'])


def build(version):
    # Leap 16 replaced the DVD image with an offline installer
    leap = f"https://download.opensuse.org/distribution/leap/{version}/offline/Leap-{version}-offline-installer-x86_64.install.iso"
    tumbleweed = "https://download.opensuse.org/tumbleweed/iso/openSUSE-Tumbleweed-DVD-x86_64-Current.iso"

    sizes = check_urls([leap, tumbleweed])

    return [
        download_data(version, url=leap, size=sizes[leap], os='linux'),
        download_data('Tumbleweed', url=tumbleweed, size=sizes[tumbleweed], os='linux'),
    ]
