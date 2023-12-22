import importlib
import json
from unittest import mock

import pytest

from pytest_sort import database


@pytest.fixture(autouse=True)
def database_file():
    importlib.reload(database)
    with mock.patch("pytest_sort.database.database_file") as database_file:
        yield database_file


@pytest.fixture()
def test_data():
    return {
        "test/test_core.py::TestClass::test_case[A]": {
            "setup": 1,
            "call": 2,
            "teardown": 3,
            "total": 6,
        },
        "test/test_core.py::TestClass::test_case[B]": {
            "setup": 11,
            "call": 21,
            "teardown": 31,
            "total": 63,
        },
    }


@pytest.fixture()
def test_file(test_data):
    return json.dumps(test_data, indent=4)


class TestLoadSave:
    def test_load_data(self, database_file, test_file, test_data):
        database_file.exists.return_value = True
        database_file.read_text.return_value = test_file

        database._load_data()

        database_file.read_text.assert_called_with("utf-8")
        assert database._sort_data == test_data

    def test_load_data_loaded(self, database_file, test_file, test_data):
        database_file.exists.return_value = True
        database_file.read_text.return_value = test_file
        database._sort_data = test_data

        database._load_data()

        database_file.read_text.assert_not_called()
        assert database._sort_data == test_data

    def test_load_data_no_file(self, database_file):
        database_file.exists.return_value = False
        database_file.read_text.return_value = None

        database._load_data()

        database_file.read_text.assert_not_called()
        assert database._sort_data == {}

    def test__save_data(self, database_file, test_file, test_data):
        database._sort_data = test_data

        database._save_data()

        database_file.write_text.assert_called_with(test_file, "utf-8")


class TestClearDb:
    @pytest.fixture()
    def save_data(self):
        with mock.patch("pytest_sort.database._save_data") as save_data:
            yield save_data

    def test_clear_db(self, save_data, test_data):
        database._sort_data = test_data
        database.clear_db()
        assert database._sort_data == {}
        save_data.assert_called()


class TestUpdate:
    @pytest.fixture(autouse=True)
    def load_data(self, test_data):
        def load_test_data():
            database._sort_data = test_data

        with mock.patch("pytest_sort.database._load_data") as load_data:
            load_data.side_effect = load_test_data
            yield load_data

    @pytest.fixture()
    def save_data(self):
        with mock.patch("pytest_sort.database._save_data") as save_data:
            save_data.side_effect = lambda: save_data.saved(database._sort_data)
            yield save_data

    def test_update_test_cases_update_less(self, save_data):
        database.update_test_cases(
            {
                "test/test_core.py::TestClass::test_case[A]": {"setup": 0, "call": 1, "teardown": 2},
            }
        )
        assert database._sort_data["test/test_core.py::TestClass::test_case[A]"] == {
            "setup": 1,
            "call": 2,
            "teardown": 3,
            "total": 6,
        }
        save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_equal(self, save_data):
        database.update_test_cases(
            {"test/test_core.py::TestClass::test_case[A]": {"setup": 1, "call": 2, "teardown": 3}}
        )
        assert database._sort_data["test/test_core.py::TestClass::test_case[A]"] == {
            "setup": 1,
            "call": 2,
            "teardown": 3,
            "total": 6,
        }
        save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_greater(self, save_data):
        database.update_test_cases(
            {
                "test/test_core.py::TestClass::test_case[A]": {"setup": 2, "call": 3, "teardown": 4},
                "test/test_core.py::TestClass::test_case[B]": {"setup": 11, "call": 22, "teardown": 31},
            }
        )
        assert database._sort_data["test/test_core.py::TestClass::test_case[A]"] == {
            "setup": 2,
            "call": 3,
            "teardown": 4,
            "total": 9,
        }
        assert database._sort_data["test/test_core.py::TestClass::test_case[B]"] == {
            "setup": 11,
            "call": 22,
            "teardown": 31,
            "total": 64,
        }
        save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_defaults(self, save_data):
        database.update_test_cases({"test/test_core.py::test_default": {}})
        assert database._sort_data["test/test_core.py::test_default"] == {
            "setup": 0,
            "call": 0,
            "teardown": 0,
            "total": 0,
        }
        save_data.saved.assert_called_with(database._sort_data)

    @pytest.mark.usefixtures("save_data")
    def test_update_test_cases_update_mock(self, test_data):
        setup = mock.MagicMock()
        call = mock.MagicMock()
        teardown = mock.MagicMock()

        node_data = {
            "setup": setup,
            "call": call,
            "teardown": teardown,
        }

        test_data["mocknode"] = node_data

        setup.__lt__ = lambda _, v: setup.lt(v)
        call.__lt__ = lambda _, v: call.lt(v)
        teardown.__lt__ = lambda _, v: teardown.lt(v)

        setup.lt.return_value = True
        call.lt.return_value = True
        teardown.lt.return_value = True

        database.update_test_cases({"mocknode": {"setup": 1, "call": 2, "teardown": 3}})

        setup.lt.assert_called_with(1)
        call.lt.assert_called_with(2)
        teardown.lt.assert_called_with(3)
        assert node_data["total"] == 6


class TestGet:
    @pytest.fixture(autouse=True)
    def load_data(self, test_data):
        def load_test_data():
            database._sort_data = test_data.copy()

        with mock.patch("pytest_sort.database._load_data") as load_data:
            load_data.side_effect = load_test_data
            yield load_data

    def test_get_all_totals(self):
        assert database.get_all_totals() == {
            "test/test_core.py::TestClass::test_case[A]": 6,
            "test/test_core.py::TestClass::test_case[B]": 63,
        }

    def test_get_bucket_total(self):
        assert database.get_bucket_total("test/test_core.py") == 69

    def test_get_bucket_total_not_found(self):
        assert database.get_bucket_total("test/test_core.py::TestOther") == 0

    def test_get_stats(self):
        assert database.get_stats("test/test_core.py::TestClass::test_case[A]") == {
            "setup": 1,
            "call": 2,
            "teardown": 3,
            "total": 6,
        }

    def test_get_stats_not_found(self):
        assert database.get_stats("test/test_core.py::test_other") == {"setup": 0, "call": 0, "teardown": 0, "total": 0}
