import handler
import utils


def test_index_lists_every_program():
    r = handler.app.test_client().get('/')

    assert r.status_code == 200
    assert r.get_json() == utils.get_all_programs()


def test_every_program_of_the_index_has_a_route():
    routes = handler.app.url_map.bind('')

    for program in utils.get_all_programs():
        routes.match('/' + program['api'])


def test_unknown_program_is_not_found():
    client = handler.app.test_client()

    assert client.get('/mozilla/nope').status_code == 404
    assert client.get('/nope').status_code == 404
