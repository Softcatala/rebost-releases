from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/sumatrapdf.json'

add_program("sumatrapdf", 'sumatrapdf', 'sumatra-pdf')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    base = f"https://www.sumatrapdfreader.org/dl/rel/{v}"

    return checked_rows(v, [
        (f"{base}/SumatraPDF-{v}-64-install.exe", 'windows', 'x86_64'),
        (f"{base}/SumatraPDF-{v}-install.exe", 'windows', 'x86'),
        (f"{base}/SumatraPDF-{v}-arm64-install.exe", 'windows', 'arm'),
    ])
