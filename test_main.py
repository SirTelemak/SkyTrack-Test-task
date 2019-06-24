import pytest
import requests

import main
import mock


@pytest.mark.parametrize('return_value, expect', ((True, True), (False, None)))
def test_update_page_table(return_value, expect):
    with mock.patch('model.Pages.add_page', return_value=return_value) as m:
        result = main.update_page_table('a', 1)
        m.assert_called_once()
    assert result == expect


def test_get_url_list():
    """
    Since it difficult to test this function, I picked random page and made some "magic" verification.
    If test fail after rewriting into asynchronous code - something is broken
    :return:
    """
    request = requests.get('https://ru.wikipedia.org/wiki/Carrissoa')
    result = main.get_url_list(request)
    expected_1 = '/wiki/Eukaryota'
    expected_2 = '/wiki/Fabaceae'

    assert len(result) == 31
    assert expected_1 in result
    assert expected_2 in result


def test_parse_page():
    # TODO: finish this test
    url = 'https://ru.wikipedia.org/wiki/Carrissoa'
    with mock.patch('main.get_url_list', return_value=['https://ru.wikipedia.org/wiki/Eukaryota',
                                                       'https://ru.wikipedia.org/wiki/Fabaceae']) as m:
        main.parse_page(url)
