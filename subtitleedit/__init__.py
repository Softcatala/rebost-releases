from utils import add_program, cached_route, download_data, get_github_release, github_asset

add_program("subtitleedit", 'subtitle-edit', 'subtitle-edit')

# (asset, arch, os); asset names carry no version
__assets = [
    ('SubtitleEdit-Windows-x64-Setup.exe', 'x86_64', 'windows'),
    ('SubtitleEdit-Windows-ARM64.zip', 'arm', 'windows'),
    ('SubtitleEdit-macOS-x64.dmg', 'x86_64', 'osx'),
    ('SubtitleEdit-macOS-ARM64.dmg', 'arm', 'osx'),
    ('SubtitleEdit-linux-x64.flatpak', 'x86_64', 'linux'),
]


@cached_route()
def get():
    return build(get_github_release('SubtitleEdit/subtitleedit', 'v'))


def build(release):
    rows = []
    for name, arch, os in __assets:
        asset = github_asset(release, name)
        # the API url already points at releases/download/<tag>/
        rows.append(download_data(release['version'], url=asset['url'], size=asset['size'], arch=arch, os=os))

    return rows
