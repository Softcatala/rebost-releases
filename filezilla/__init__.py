from utils import add_program, cached_route, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/filezilla.json'

# direct links carry a token that expires, so every row is a landing page
landing = 'https://filezilla-project.org/download.php?show_all=1'

add_program("filezilla", 'filezilla', 'filezilla')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(version):
    return [
        download_data(version, url=landing, arch='generic', os=os)
        for os in ('windows', 'osx', 'linux')
    ]
