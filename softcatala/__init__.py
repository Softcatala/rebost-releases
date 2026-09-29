from utils import add_program, cached_route, download_data, get_github_release, github_asset

# program: (repository, tag prefix, [(asset name, version label suffix)])
programs = {
    'dict-ca': ('Softcatala/catalan-dict-tools', 'v', [('ca.{v}.oxt', '')]),
    'dict-ca-valencia': ('Softcatala/catalan-dict-tools', 'v', [('ca-valencia.{v}.oxt', '')]),
    'thesaurus': ('Softcatala/sinonims-cat', '', [('thesaurus-ca.oxt', '')]),
    'hyphen': ('jaumeortola/hyphen-ca', 'v', [('hyph-ca.oxt', ''), ('hyph_ca_ES.dic', ' (TXT)')]),
}

add_program("softcatala", 'softcatala/dict-ca', 'corrector-ortografic-de-catala-general-per-al-libreoffice-i-lapache-openoffice')
add_program("softcatala", 'softcatala/dict-ca-valencia', 'corrector-ortografic-de-catala-valencia-per-al-libreoffice-i-lapache-openoffice')
add_program("softcatala", 'softcatala/thesaurus', 'diccionari-catala-de-sinonims-per-al-libreoffice')
add_program("softcatala", 'softcatala/hyphen', 'diccionari-catala-de-particio-de-mots')


@cached_route()
def get(program):
    if program not in programs:
        return None

    repo, prefix, assets = programs[program]

    return build(get_github_release(repo, prefix), assets)


def build(release, assets):
    version = release['version']

    rows = []
    for name, label in assets:
        asset = github_asset(release, name.format(v=version))
        rows.append(download_data(
            f"{version}{label}",
            url=asset['url'],
            size=asset['size'],
            arch='generic',
            os='multiplataforma',
        ))

    return rows

