from cachetools import cached, TTLCache

from .ubuntu import __desktop, __other


@cached(cache=TTLCache(maxsize=10, ttl=300))
def get(flavor):
    try:
        if flavor == 'ubuntu':
            return __desktop()
        else:
            return __other(flavor)
    except:
        pass

    return None
