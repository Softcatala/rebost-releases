from utils import add_program, cached_route, checked_rows, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/krita.json'

add_program("kde", 'krita', 'krita')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    base = f"https://download.kde.org/stable/krita/{v}"

    return checked_rows(v, [
        (f"{base}/krita-x64-{v}-setup.exe", 'windows', 'generic'),
        (f"{base}/krita-{v}-signed.dmg", 'osx', 'generic'),
    ]) + [
        download_data(v, url="appstream://org.kde.krita", os='linux'),
        download_data(v, url="https://play.google.com/store/apps/details?id=org.krita",
                      arch='generic', os='android'),
    ]
