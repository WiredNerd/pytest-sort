from unittest import mock

from test_var import core

response_1 = {"next": "2", "values": [1]}
response_2 = {"next": "3", "values": [2]}
response_3 = {"next": "", "values": [3]}


@mock.patch("test_var.core.get_values")
def test_get_all_values_no_next(get_values):
    get_values.return_value = response_3
    assert core.get_all_values() == [3]


@mock.patch("test_var.core.get_values")
def test_get_all_values_one_loop(get_values):
    get_values.side_effect = [response_2, response_3]
    assert core.get_all_values() == [2, 3]


@mock.patch("test_var.core.get_values")
def test_get_all_values_two_loops(get_values):
    get_values.side_effect = [response_1, response_2, response_3]
    assert core.get_all_values() == [1, 2, 3]
