import importlib
import os
from unittest import mock

import pytest

from module_var import app


@pytest.fixture()  # Fixture to set environment variables, and reset after testing
def environment_variables():
    vars = {"DB_USERNAME": "test_user"}
    with mock.patch.dict(os.environ, vars):
        importlib.reload(app)
        yield vars
    importlib.reload(app)


def test_default_username():
    assert app.USERNAME == "default"


def test_username(environment_variables):
    assert app.USERNAME == environment_variables["DB_USERNAME"]


def test_get_username():
    assert app.get_username() == "default"
