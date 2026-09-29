from utils import add_program, cached_route, checked_rows, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/digikam.json'

add_program("kde", 'digikam', 'digikam')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    base = f"https://download.kde.org/stable/digikam/{v}"

    # the Intel macOS build is still the Qt5 one
    return checked_rows(v, [
        (f"{base}/digiKam-{v}-Qt6-Win64.exe", 'windows', 'x86_64'),
        (f"{base}/digiKam-{v}-Qt5-MacOS-x86_64.pkg", 'osx', 'x86_64'),
        (f"{base}/digiKam-{v}-Qt6-MacOS-arm64.pkg", 'osx', 'arm'),
    ]) + [
        download_data(v, url="https://www.digikam.org/download/binary/#Linux", os='linux'),
    ]
