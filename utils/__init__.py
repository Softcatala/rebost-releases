import math
from typing import Dict

import feedparser
import requests

import re

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
    r = requests.get(url)

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