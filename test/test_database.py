import importlib
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

import pytest
from pony.orm import OperationalError, db_session

import pytest_sort.database as database


@pytest.fixture(autouse=True)
def reset():
    importlib.reload(database)


@pytest.fixture
def db():
    with mock.patch("pytest_sort.database.db") as db:
        yield db


class TestInitDb:
    @database._init_db
    def init_db(self):
        pass

    def test_init_db(self, db: MagicMock):
        db.provider = None

        self.init_db()

        db_path_filename = str(Path.cwd() / ".pytest_sort")
        db.bind.assert_called_with(provider="sqlite", filename=db_path_filename, create_db=True)
        db.generate_mapping.assert_called_with(create_tables=True)

    def test_init_db_fix_db(self, db: MagicMock):
        db.provider = None
        db.generate_mapping.side_effect = [OperationalError(Exception()), None]

        self.init_db()

        db_path_filename = str(Path.cwd() / ".pytest_sort")
        db.bind.assert_called_with(provider="sqlite", filename=db_path_filename, create_db=True)
        db.generate_mapping.assert_has_calls(
            [
                mock.call(create_tables=True),
                mock.call(create_tables=True),
            ]
        )
        db.drop_all_tables.assert_called_with(with_all_data=True)
        assert db.schema is None

    def test_init_db_already_created(self, db: MagicMock):
        db.provider = "sqlite"

        self.init_db()

        db.bind.assert_not_called()
        db.generate_mapping.assert_not_called()


class TestClearDb:
    def test_clear_db(self):
        database.clear_db()
        with db_session:
            database.TestTab(nodeid="fake", setup=0, call=0, teardown=0, total=0)
        database.clear_db()
        with db_session:
            assert database.TestTab.select().fetch().to_list() == []

    def test_clear_db_mock(self, db):
        db.schema = "test"
        database.clear_db()
        db.drop_all_tables.assert_called_with(with_all_data=True)
        assert db.schema == None
        db.generate_mapping.assert_called_with(create_tables=True)


class TestUpdate:
    @pytest.fixture(autouse=True)
    def clear_db(self):
        database.clear_db()
        yield

    def test_update_test_case_default(self):
        database.update_test_case("test_node_1")
        with db_session:
            row = database.TestTab.select().first().to_dict()
            assert row == {"nodeid": "test_node_1", "setup": 0, "call": 0, "teardown": 0, "total": 0}

    def test_update_test_case_values(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        with db_session:
            row = database.TestTab.select().first().to_dict()
            assert row == {"nodeid": "test_node_1", "setup": 3, "call": 2, "teardown": 5, "total": 10}

    def test_update_test_case_less(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        database.update_test_case("test_node_1", setup=2, call=1, teardown=4)
        with db_session:
            row = database.TestTab.select().first().to_dict()
            assert row == {"nodeid": "test_node_1", "setup": 3, "call": 2, "teardown": 5, "total": 10}

    def test_update_test_case_equal(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        with db_session:
            row = database.TestTab.select().first().to_dict()
            assert row == {"nodeid": "test_node_1", "setup": 3, "call": 2, "teardown": 5, "total": 10}

    def test_update_test_case_greater(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        database.update_test_case("test_node_1", setup=4, call=3, teardown=6)
        with db_session:
            row = database.TestTab.select().first().to_dict()
            assert row == {"nodeid": "test_node_1", "setup": 4, "call": 3, "teardown": 6, "total": 13}

    def test_update_test_case_mock(self, db):
        with mock.patch("pytest_sort.database.TestTab") as TestTab:
            test = TestTab.get.return_value
            test.setup.__lt__ = lambda self, v: test.setup_lt(v)
            test.call.__lt__ = lambda self, v: test.call_lt(v)
            test.teardown.__lt__ = lambda self, v: test.teardown_lt(v)
            test.total.__lt__ = lambda self, v: test.total_lt(v)

            database.update_test_case("test_node_1", 1, 2, 3)

            test.setup_lt.assert_called_with(1)
            assert test.setup == 1
            test.call_lt.assert_called_with(2)
            assert test.call == 2
            test.teardown_lt.assert_called_with(3)
            assert test.teardown == 3
            test.total_lt.assert_called_with(6)
            assert test.total == 6

    def test_update_test_case_init_db(self, db):
        db.provider = None
        database.update_test_case("test_node_1")
        db.bind.assert_called()


class TestGet:
    @pytest.fixture(autouse=True)
    def clear_db(self):
        database.clear_db()
        yield

    def test_get_total(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        assert database.get_total("test_node_1") == 10

    def test_get_total_not_found(self):
        assert database.get_total("test_node_1") == 0

    def test_get_total_init_db(self, db):
        db.provider = None
        database.get_total("test_node_1")
        db.bind.assert_called()

    def test_get_all_totals(self):
        database.update_test_case("test_node_1", call=2)
        database.update_test_case("test_node_2", call=3)
        assert database.get_all_totals() == {
            "test_node_1": 2,
            "test_node_2": 3,
        }

    def test_get_all_totals_init_db(self, db):
        db.provider = None
        database.get_all_totals()
        db.bind.assert_called()

    def test_get_bucket_total(self):
        database.update_test_case("test_node_1", call=2)
        database.update_test_case("test_node_2", call=3)
        database.update_test_case("other_node_1", call=4)
        database.update_test_case("other_node_2", call=5)

        assert database.get_bucket_total("test") == 5

    def test_get_bucket_total_not_found(self):
        database.update_test_case("test_node_1", call=2)
        database.update_test_case("test_node_2", call=3)
        database.update_test_case("other_node_1", call=4)
        database.update_test_case("other_node_2", call=5)

        assert database.get_bucket_total("not") == 0

    def test_get_bucket_total_init_db(self, db):
        db.provider = None
        database.get_bucket_total("test")
        db.bind.assert_called()

    def test_get_stats(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        assert database.get_stats("test_node_1") == {"setup": 3, "call": 2, "teardown": 5, "total": 10}

    def test_get_stats_not_found(self):
        database.update_test_case("test_node_1", setup=3, call=2, teardown=5)
        assert database.get_stats("test_node_2") == {"setup": 0, "call": 0, "teardown": 0, "total": 0}

    def test_get_stats_init_db(self, db):
        db.provider = None
        database.get_stats("test_node_1")
        db.bind.assert_called()
