from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/kdenlive.json'

add_program("kde", 'kdenlive', 'kdenlive')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    major, minor = v.split('.')[:2]
    base = f"https://download.kde.org/stable/kdenlive/{major}.{minor}"

    return checked_rows(v, [
        (f"{base}/windows/kdenlive-{v}.exe", 'windows', 'generic'),
        (f"{base}/macOS/kdenlive-{v}-x86_64.dmg", 'osx', 'x86_64'),
        (f"{base}/macOS/kdenlive-{v}-arm64.dmg", 'osx', 'arm'),
        (f"{base}/linux/kdenlive-{v}-x86_64.AppImage", 'linux', 'x86_64'),
    ])
