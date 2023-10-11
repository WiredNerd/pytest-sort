from unittest import mock

import pytest

from test_var import core


@pytest.fixture()
def responses():
    return (
        {"next": "2", "values": [1]},
        {"next": "3", "values": [2]},
        {"next": "", "values": [3]},
    )


@mock.patch("test_var.core.get_values")
def test_get_all_values_no_next(get_values, responses):
    get_values.return_value = responses[2]
    assert core.get_all_values() == [3]


@mock.patch("test_var.core.get_values")
def test_get_all_values_one_loop(get_values, responses):
    get_values.side_effect = [responses[1], responses[2]]
    assert core.get_all_values() == [2, 3]


@mock.patch("test_var.core.get_values")
def test_get_all_values_two_loops(get_values, responses):
    get_values.side_effect = [responses[0], responses[1], responses[2]]
    assert core.get_all_values() == [1, 2, 3]
