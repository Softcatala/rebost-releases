import json
from pathlib import Path

import pytest

import github
from utils import parse_github_release

FIXTURES = Path(__file__).parent / 'fixtures' / 'github'

REPOS = {name: cfg['repo'] for name, cfg in github.programs.items()}


def load(program):
    config = github.programs[program]
    js = json.loads((FIXTURES / (config['repo'].replace('/', '_') + '.json')).read_text())
    return config, parse_github_release(js, config['tag_prefix'])


@pytest.mark.parametrize('program', sorted(github.programs))
def test_every_program_builds_from_its_fixture(program):
    config, release = load(program)

    rows = github.build(config, release)

    assert len(rows) == len(config['assets']) + len(config.get('static', []))
    assert all(r['download_version'] != '' or r['download_os'] in ('android', 'ios') for r in rows)
    # every discovered row links to a GitHub release asset and carries a size
    for r in rows[:len(config['assets'])]:
        assert r['download_url'].startswith('https://github.com/')
        assert r['download_size']


def test_seventeen_programs_registered():
    assert len(github.programs) == 17


def test_musescore_shows_tag_version_not_build_number():
    config, release = load('musescore')

    rows = github.build(config, release)

    assert {r['download_version'] for r in rows if r['download_os'] in ('windows', 'osx', 'linux')} == {'4.7.5'}
    assert '4.7.5.260831071' in rows[0]['download_url']


def test_geany_reads_version_from_asset_name():
    config, release = load('geany')

    rows = github.build(config, release)

    assert release['version'] == '2.1.0'
    assert rows[0]['download_version'] == '2.1'


def test_librecad_windows_32_and_64_do_not_collide():
    config, release = load('librecad')

    rows = {(r['download_os'], r['arquitectura']): r['download_url'] for r in github.build(config, release)}

    assert rows[('windows', 'x86_64')].endswith('-win64-msvc.exe')
    assert rows[('windows', 'x86')].endswith('-msvc.exe') and 'win64' not in rows[('windows', 'x86')]


def test_joplin_intel_dmg_has_no_arch_in_name():
    config, release = load('joplin')

    rows = {(r['download_os'], r['arquitectura']): r['download_url'] for r in github.build(config, release)}

    assert rows[('osx', 'x86_64')].endswith('Joplin-3.7.21.dmg')
    assert rows[('osx', 'arm')].endswith('-arm64.DMG')


def test_cryptomator_msi_gets_label():
    config, release = load('cryptomator')

    versions = [r['download_version'] for r in github.build(config, release)]

    assert '1.19.3 (MSI)' in versions


def test_static_rows_are_kept():
    config, release = load('drawio')

    rows = github.build(config, release)

    assert rows[-1]['download_os'] == 'web'
    assert rows[-1]['download_url'] == 'https://app.diagrams.net/'


def test_pattern_matching_nothing_fails():
    config, release = load('gnucash')
    release['assets'].pop('gnucash-5.17.setup.exe')

    with pytest.raises(ValueError):
        github.build(config, release)


def test_pattern_matching_several_fails():
    config, release = load('gnucash')
    release['assets']['gnucash-5.17.setup.EXE'] = release['assets']['gnucash-5.17.setup.exe']

    with pytest.raises(ValueError):
        github.build(config, release)


def test_one_broken_program_does_not_affect_others(monkeypatch):
    config, release = load('gnucash')
    release['assets'].clear()
    calls = {'gnucash': release, 'sigil': load('sigil')[1]}
    monkeypatch.setattr(github, 'get_github_release',
                        lambda repo, prefix: calls['gnucash'] if 'gnucash' in repo else calls['sigil'])

    assert github.get('gnucash') is None
    assert len(github.get('sigil')) == 4
