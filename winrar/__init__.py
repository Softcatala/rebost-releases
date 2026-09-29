from utils import add_program, cached_route, check_urls, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/winrar.json'

add_program("winrar", 'winrar', 'winrar')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(version):
    # the Catalan build can appear later than the English one: the check
    # fails, and WordPress keeps the rows it has
    url = f"https://www.rarlab.com/rar/winrar-x64-{version.replace('.', '')}ca.exe"
    sizes = check_urls([url])

    return [
        download_data(version, url=url, size=sizes[url], arch='x86_64', os='windows'),
        download_data(
            version,
            url='https://play.google.com/store/apps/details?id=com.rarlab.rar&hl=ca',
            arch='generic',
            os='android',
        ),
    ]
