from utils import add_program, cached_route, download_data, get_scoop

scoop_url = 'https://raw.githubusercontent.com/ScoopInstaller/Extras/master/bucket/vlc.json'

add_program("vlc", 'vlc', 'vlc-media-player')


@cached_route()
def get():
    return build(get_scoop(scoop_url)['version'])


def build(v):
    # get.videolan.org links are mirror redirector pages (HTML), so they are
    # declared as landing rows and not validated
    base = f"https://get.videolan.org/vlc/{v}"

    return [
        download_data(v, url=f"{base}/win64/vlc-{v}-win64.exe", arch='x86_64', os='windows'),
        download_data(v, url=f"{base}/win32/vlc-{v}-win32.exe", arch='x86', os='windows'),
        download_data(v, url=f"{base}/macosx/vlc-{v}-universal.dmg", arch='generic', os='osx'),
        download_data(v, url='https://www.videolan.org/vlc/#download', arch='generic', os='linux'),
        download_data(v, url='https://play.google.com/store/apps/details?id=org.videolan.vlc',
                      arch='generic', os='android'),
        download_data(v, url='https://apps.apple.com/app/vlc-for-mobile/id650377962',
                      arch='generic', os='ios'),
    ]
