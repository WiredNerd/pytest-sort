import os
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

from pony.orm import db_session

import pytest_sort.database as database


class TestInitDb:
    @database._init_db
    def init_db(self):
        pass

    @mock.patch("pytest_sort.database.db")
    def test_init_db(self, db: MagicMock):
        db.provider = None

        self.init_db()

        db_path_filename = str(Path.cwd() / ".pytest_sort")
        db.bind.assert_called_with(provider="sqlite", filename=db_path_filename, create_db=True)
        db.generate_mapping.assert_called_with(create_tables=True)

    @mock.patch("pytest_sort.database.db")
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
