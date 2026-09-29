import functools
import math
import os as _os
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

import feedparser
import requests
from cachetools import TTLCache

import re

# WordPress gives each route 5 seconds, so upstream calls must be short
REQUEST_TIMEOUT = 3

def get_content_size(url):
    r = requests.head(url,allow_redirects=True)
    return r.headers["Content-Length"]


def get_debian_package(package):
    url = f'https://sources.debian.org/api/src/{package}/'

    r = requests.get(url)

    js = r.json()

    versions = js['versions']

    sid = [v for v in versions if 'sid' in v['suites']]

    if not sid:
        return

    item = next(v for v in sid if '~' not in v['version'])
    latest = item['version']

    m = re.search(':(.+?)-', latest)

    if m:
        version = m.group(1)

        parts = version.split('.')

        js = {}
        js['version'] = version
        js['majorVersion'] = parts[0]
        if len(parts) > 1:
            js['minorVersion'] = parts[1]
        if len(parts) > 2:
            js['patchVersion'] = parts[2]

        return js

def get_scoop(url):
    r = requests.get(url, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    js = r.json()

    version = js['version']

    parts = version.split('.')

    js['majorVersion'] = parts[0]
    if len(parts) > 1:
        js['minorVersion'] = parts[1]
    if len(parts) > 2:
        js['patchVersion'] = parts[2]

    return js


def get_gitlab_tag_rss(url, filter):
    feed = feedparser.parse(url)

    title = feed.entries[0].title

    version = {}
    if filter:
        version['version'] = title.replace(filter, '')
    else:
        version['version'] = title

    parts = version['version'].split('.')

    version['majorVersion'] = parts[0]
    if len(parts) > 1:
        version['minorVersion'] = parts[1]
    if len(parts) > 2:
        version['patchVersion'] = parts[2]

    return version


def download_data(version, url, size="", arch="generic", os="multiplataforma", get_size=False, human_size=""):

    if get_size:
        try:
            size = get_content_size(url)
        except:
            pass

    if human_size == "" and size:
        human_size = __from_bytes_to_human(size)

    return {
        'download_version': version,
        'download_url': url,
        'download_size': human_size,
        'arquitectura': arch,
        'download_os': os
    }


def __from_bytes_to_human(size):

    log = math.log(int(size), __base)

    fixed = math.floor(log)
    exp = log - fixed

    precision = 2 if fixed > 1 else 1

    n = round( math.pow(__base, exp), precision)

    return f"{n:g} {__size_units[fixed]}".strip()


__size_units = [
    "", "KB", "MB", "GB","TB"
]

__base = 1024


programs = []


def add_program(group, api, wp):
    programs.append({'wp': wp, 'api': api, 'group': group})


def get_all_programs():
    return programs


def get_eol_date(program):
    url = f'https://endoflife.date/api/{program}.json'

    r = requests.get(url)

    js = r.json()

    return js[0]


def cached_route(ttl=300):
    """Caches the result of a route function. A failure (exception) or an
    empty result is logged as such, answered with None and never cached, so the
    route recovers as soon as upstream does."""
    def decorator(fn):
        cache = TTLCache(maxsize=32, ttl=ttl)

        @functools.wraps(fn)
        def wrapper(*args):
            if args in cache:
                return cache[args]

            try:
                result = fn(*args)
            except Exception as e:
                print(f"{fn.__module__}{args or ''}: {e!r}")
                return None

            if not result:
                print(f"{fn.__module__}{args or ''}: no data")
                return None

            cache[args] = result
            return result

        return wrapper
    return decorator


class BrokenUrl(Exception):
    pass


def __probe(url):
    """Returns the size in bytes ('' when unknown) if the url resolves to a
    file, None otherwise. Some hosts reject HEAD, so fall back to a one-byte
    ranged GET."""
    # a mirror that compresses what it sends does not say how big the file is
    as_is = {'Accept-Encoding': 'identity'}

    try:
        r = requests.head(url, headers=as_is, allow_redirects=True, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200 and not __is_html(r):
            return r.headers.get('Content-Length', '')
    except requests.RequestException:
        pass

    try:
        r = requests.get(url, headers={'Range': 'bytes=0-0', **as_is}, stream=True,
                         allow_redirects=True, timeout=REQUEST_TIMEOUT)
        r.close()
        if r.status_code not in (200, 206) or __is_html(r):
            return None

        total = r.headers.get('Content-Range', '').rpartition('/')[2]
        if total.isdigit():
            return total
        return r.headers.get('Content-Length', '') if r.status_code == 200 else ''
    except requests.RequestException:
        return None


def __is_html(response):
    return response.headers.get('Content-Type', '').startswith('text/html')


def check_urls(urls):
    """Checks in parallel that every url resolves to a file. Returns
    {url: size} and raises BrokenUrl when any of them does not."""
    urls = list(dict.fromkeys(urls))

    with ThreadPoolExecutor(max_workers=max(len(urls), 1)) as pool:
        sizes = list(pool.map(__probe, urls))

    broken = [u for u, s in zip(urls, sizes) if s is None]
    if broken:
        raise BrokenUrl(f"does not resolve to a file: {', '.join(broken)}")

    return dict(zip(urls, sizes))


def get_github_release(repo, tag_prefix=''):
    """Latest release of a GitHub repository: the tag, the version (tag
    without prefix) and the assets as {name: {'url', 'size'}}."""
    headers = {'Accept': 'application/vnd.github+json'}
    token = _os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'

    r = requests.get(f'https://api.github.com/repos/{repo}/releases/latest',
                     headers=headers, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return parse_github_release(r.json(), tag_prefix)


def parse_github_release(js, tag_prefix=''):
    tag = js['tag_name']
    version = tag[len(tag_prefix):] if tag.startswith(tag_prefix) else tag

    return {
        'tag': tag,
        'version': version,
        'assets': {
            a['name']: {'url': a['browser_download_url'], 'size': a['size']}
            for a in js.get('assets', [])
        },
    }


def github_asset(release, name):
    try:
        return release['assets'][name]
    except KeyError:
        raise ValueError(f"release {release['tag']} has no asset {name}")


def get_amo_addon(id_or_slug):
    """Current version of a Mozilla add-on: {'version', 'url', 'size'}."""
    r = requests.get(f'https://addons.mozilla.org/api/v5/addons/addon/{id_or_slug}/',
                     timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return parse_amo_addon(r.json())


def parse_amo_addon(js):
    current = js['current_version']

    return {
        'version': current['version'],
        'url': js.get('url', ''),
        'size': (current.get('file') or {}).get('size', ''),
    }


def checked_rows(version, specs):
    """Rows for urls built from a vendor pattern. specs are
    (url, os, arch[, version label suffix]); the urls must all resolve to
    files, or BrokenUrl is raised and the route answers NoData."""
    sizes = check_urls([spec[0] for spec in specs])

    return [
        download_data(f"{version}{spec[3] if len(spec) > 3 else ''}",
                      url=spec[0], size=sizes[spec[0]], os=spec[1], arch=spec[2])
        for spec in specs
    ]
