from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/keepass.json'

add_program("keepass", 'keepass', 'keepass')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    url = f"https://downloads.sourceforge.net/project/keepass/KeePass%202.x/{v}/KeePass-{v}-Setup.exe"

    return checked_rows(v, [(url, 'windows', 'generic')])
