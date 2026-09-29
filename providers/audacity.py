from utils import add_program, cached_route, download_data, get_github_release, github_asset

add_program("audacity", 'audacity', 'audacity')


@cached_route()
def get():
    return build(get_github_release('audacity/audacity', 'Audacity-'))


def build(release):
    v = release['version']

    assets = [
        (f'audacity-win-{v}-x86_64.msi', 'x86_64', 'windows'),
        (f'audacity-win-{v}-arm64.msi', 'arm', 'windows'),
        (f'audacity-macOS-{v}-universal.dmg', 'generic', 'osx'),
        (f'audacity-linux-{v}-x86_64.AppImage', 'x86_64', 'linux'),
    ]

    rows = []
    for name, arch, os in assets:
        asset = github_asset(release, name)
        rows.append(download_data(v, url=asset['url'], size=asset['size'], arch=arch, os=os))

    return rows
