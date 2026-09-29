from utils import add_program, cached_route, checked_rows, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/blender.json'

add_program("blender", 'blender', 'blender')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    major, minor = v.split('.')[:2]
    base = f"https://download.blender.org/release/Blender{major}.{minor}"

    # there is no Intel macOS build any more
    return checked_rows(v, [
        (f"{base}/blender-{v}-windows-x64.msi", 'windows', 'x86_64'),
        (f"{base}/blender-{v}-macos-arm64.dmg", 'osx', 'arm'),
        (f"{base}/blender-{v}-linux-x64.tar.xz", 'linux', 'x86_64'),
    ])
