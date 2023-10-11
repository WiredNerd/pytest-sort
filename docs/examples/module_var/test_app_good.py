import importlib
import os
from unittest import mock

from module_var import app


def test_default_username():
    importlib.reload(app)  # Reload defaults before Testing
    assert app.USERNAME == "default"


def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
    assert app.USERNAME == "test_user"


def test_get_username():
    app.USERNAME = "example_user"  # Set expected value
    assert app.get_username() == "example_user"
