import requests

from utils import REQUEST_TIMEOUT, add_program, cached_route, check_urls, download_data

products_url = ('https://rdc.adobe.io/reader/products?lang=ca&site=enterprise&os=Windows%2011'
                '&country=ES&nativeOs=Windows%2010&api_key=dc-get-adobereader-cdn')

add_program("adobe", 'adobe-reader', 'adobe-acrobat-reader')


@cached_route()
def get():
    r = requests.get(products_url, headers={'x-api-key': 'dc-get-adobereader-cdn'},
                     timeout=REQUEST_TIMEOUT)
    r.raise_for_status()

    return build(parse_version(r.json()))


def parse_version(js):
    return js['products']['reader'][0]['version']


def build(adobe_version):
    """adobe_version is the feed's version, e.g. 26.002.21931."""
    digits = adobe_version.replace('.', '')
    url = f"https://ardownload3.adobe.com/pub/adobe/reader/win/AcrobatDC/{digits}/AcroRdrDC{digits}_ca_ES.exe"
    sizes = check_urls([url])

    # the page shows the version with the year prefix in full
    return [
        download_data(f"20{adobe_version}", url=url, size=sizes[url], arch='x86', os='windows'),
    ]
