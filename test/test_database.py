import importlib
import json
from unittest import mock

import pytest

import pytest_sort.database as database


@pytest.fixture(autouse=True)
def reset():
    importlib.reload(database)


@pytest.fixture(autouse=True)
def database_file(reset):
    with mock.patch("pytest_sort.database.database_file") as database_file:
        yield database_file


@pytest.fixture
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


@pytest.fixture
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
    @pytest.fixture
    def _save_data(self):
        with mock.patch("pytest_sort.database._save_data") as _save_data:
            yield _save_data

    def test_clear_db(self, _save_data, test_data):
        database._sort_data = test_data
        database.clear_db()
        assert database._sort_data == {}
        _save_data.assert_called()


class TestUpdate:
    @pytest.fixture(autouse=True)
    def _load_data(self, test_data):
        def load_test_data():
            database._sort_data = test_data.copy()

        with mock.patch("pytest_sort.database._load_data") as _load_data:
            _load_data.side_effect = load_test_data
            yield _load_data

    @pytest.fixture
    def _save_data(self):
        with mock.patch("pytest_sort.database._save_data") as _save_data:
            _save_data.side_effect = lambda: _save_data.saved(database._sort_data)
            yield _save_data

    def test_update_test_cases_update_less(self, _save_data):
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
        _save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_equal(self, _save_data):
        database.update_test_cases(
            {"test/test_core.py::TestClass::test_case[A]": {"setup": 1, "call": 2, "teardown": 3}}
        )
        assert database._sort_data["test/test_core.py::TestClass::test_case[A]"] == {
            "setup": 1,
            "call": 2,
            "teardown": 3,
            "total": 6,
        }
        _save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_greater(self, _save_data):
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
        _save_data.saved.assert_called_with(database._sort_data)

    def test_update_test_cases_update_defaults(self, _save_data):
        database.update_test_cases({"test/test_core.py::test_default": {}})
        assert database._sort_data["test/test_core.py::test_default"] == {
            "setup": 0,
            "call": 0,
            "teardown": 0,
            "total": 0,
        }
        _save_data.saved.assert_called_with(database._sort_data)


class TestGet:
    @pytest.fixture(autouse=True)
    def _load_data(self, test_data):
        def load_test_data():
            database._sort_data = test_data.copy()

        with mock.patch("pytest_sort.database._load_data") as _load_data:
            _load_data.side_effect = load_test_data
            yield _load_data

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
