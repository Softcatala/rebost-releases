from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/opera.json'

add_program("opera", 'opera', 'opera')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    base = f"https://get.geo.opera.com/pub/opera/desktop/{v}"

    return checked_rows(v, [
        (f"{base}/win/Opera_{v}_Setup_x64.exe", 'windows', 'x86_64'),
        (f"{base}/win/Opera_{v}_Setup.exe", 'windows', 'x86'),
        (f"{base}/mac/Opera_{v}_Setup.dmg", 'osx', 'generic'),
    ])
