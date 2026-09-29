from utils import add_program, cached_route, checked_rows, download_data, get_gitlab_tag_rss

gitlab_tags_rss = 'https://invent.kde.org/education/gcompris/-/tags?format=atom'

add_program("kde", 'gcompris', 'gcompris')


@cached_route()
def get():
    return build(get_gitlab_tag_rss(gitlab_tags_rss, 'V')['version'])


def build(v):
    # there are no 32-bit Windows or macOS builds any more
    return checked_rows(v, [
        (f"https://gcompris.net/download/qt/windows/gcompris-qt-{v}-win64-gcc.exe", 'windows', 'x86_64'),
    ]) + [
        download_data(v, url="https://gcompris.net/downloads-ca.html#linux", os='linux'),
        download_data(v, url="https://play.google.com/store/apps/details?id=net.gcompris.full",
                      arch='generic', os='android'),
    ]
