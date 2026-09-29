import re

import pytest

from providers.ubuntu import iso, releases

META = """Dist: bionic
Name: Bionic Beaver
Version: 18.04.6 LTS
Supported: 1
Description: This is the 18.04 LTS release

Dist: questing
Name: Questing Quokka
Version: 25.10
Supported: 0
Description: This is the 25.10 release

"""

SHA256SUMS = [
    "xubuntu-24.04.3-desktop-amd64.iso",
    "xubuntu-24.04.3-minimal-amd64.iso",
    "xubuntu-24.04.10-desktop-amd64.iso",
    "xubuntu-24.04.4-desktop-amd64.iso",
    "xubuntu-24.04.4-minimal-amd64.iso",
]


def test_parse_reads_every_record():
    found = list(releases.parse(META))

    assert [r['codename'] for r in found] == ['bionic', 'questing']


def test_parse_marks_lts_and_support():
    bionic, questing = list(releases.parse(META))

    assert bionic == {
        'codename': 'bionic',
        'version': '18.04.6',
        'compare': 1804,
        'lts': True,
        'dev': False,
        'supported': True
    }
    assert not questing['lts']
    assert not questing['supported']


@pytest.mark.parametrize("a,b", [
    ("24.04.4", "24.04.3"),
    ("24.04.10", "24.04.4"),
    ("24.04.1", "24.04"),
    ("26.04", "24.04.4"),
])
def test_compare_orders_versions(a, b):
    assert iso.compare(a) > iso.compare(b)


def test_newest_picks_the_highest_point_release():
    pattern = re.compile(r"^xubuntu-(.+?)-desktop-amd64\.iso$")

    assert iso.newest(SHA256SUMS, pattern) == (
        "24.04.10", "xubuntu-24.04.10-desktop-amd64.iso"
    )


def test_newest_ignores_other_varieties():
    pattern = re.compile(r"^xubuntu-(.+?)-minimal-amd64\.iso$")

    assert iso.newest(SHA256SUMS, pattern) == (
        "24.04.4", "xubuntu-24.04.4-minimal-amd64.iso"
    )


def test_newest_returns_none_when_nothing_matches():
    assert iso.newest(SHA256SUMS, re.compile(r"^kubuntu-(.+?)\.iso$")) is None
