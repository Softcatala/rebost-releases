from utils import add_program, cached_route, checked_rows, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/poedit.json'
landing = 'https://poedit.net/download'

add_program("poedit", 'poedit', 'poedit')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    # download.poedit.net rejects HEAD; check_urls falls back to a ranged GET
    rows = checked_rows(v, [(f"https://download.poedit.net/Poedit-{v}-setup.exe", 'windows', 'generic')])

    rows += [download_data(v, url=landing, arch='generic', os=os) for os in ('osx', 'linux')]

    return rows
