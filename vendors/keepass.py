from utils import cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/keepass.json'

# Not registered with add_program on purpose: the page documents KeePass 1.x,
# and moving it to 2.x has to be confirmed first. To enable it, add
#   add_program("keepass", 'keepass', 'keepass')
# and the route in handler.py already exists.


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    url = f"https://downloads.sourceforge.net/project/keepass/KeePass%202.x/{v}/KeePass-{v}-Setup.exe"

    return checked_rows(v, [(url, 'windows', 'generic')])
