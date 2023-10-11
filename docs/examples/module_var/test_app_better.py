import importlib
import os
from unittest import mock

import pytest

from module_var import app


@pytest.fixture(autouse=True)  # Fixture to reset app module
def _reset_data():
    importlib.reload(app)


def test_default_username():
    assert app.USERNAME == "default"


def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
    assert app.USERNAME == "test_user"


def test_get_username():
    assert app.get_username() == "default"
