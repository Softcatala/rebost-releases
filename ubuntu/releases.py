from ubuntu_release_info import data


def __all():
    d = data.Data()

    a = [__info(r) for r in d.supported]

    return sorted(a, key=lambda x: x['compare'], reverse=True)


def __info(r):
    return {
        'codename': r.codename,
        'version': r.version,
        'compare': r.year * 100 + r.month,
        'lts': r.is_lts,
        'dev': r.is_dev
    }