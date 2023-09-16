"""Manages pony database for pytest_sort plugin."""

from __future__ import annotations

from functools import wraps
from pathlib import Path
from typing import Any, Callable

from pony.orm import Database, OperationalError, PrimaryKey, Required, db_session

database_file = Path.cwd() / ".pytest_sort"
db = Database()


class TestTab(db.Entity):  # type: ignore[name-defined]
    """Records data for each Test Case by nodeid."""

    nodeid = PrimaryKey(str)
    setup = Required(int, size=64)
    call = Required(int, size=64)
    teardown = Required(int, size=64)
    total = Required(int, size=64)


def _init_db(f: Callable) -> Callable:
    """Initialize database before running function."""

    @wraps(f)  # pragma: no mutate
    def wrapper(*args: tuple, **kwargs: dict[str, Any]):  # noqa: ANN202
        if not db.provider:
            db.bind(provider="sqlite", filename=str(database_file), create_db=True)
            try:
                db.generate_mapping(create_tables=True)
            except OperationalError:
                db.drop_all_tables(with_all_data=True)
                db.schema = None  # Pony will only rebuild build tables if this is None
                db.generate_mapping(create_tables=True)
        return f(*args, **kwargs)

    return wrapper


@_init_db
def clear_db() -> None:
    """Manually drop and recreate tables."""
    db.drop_all_tables(with_all_data=True)
    db.schema = None  # Pony will only rebuild build tables if this is None
    db.generate_mapping(create_tables=True)


@_init_db
@db_session
def update_test_case(nodeid: str, setup: int = 0, call: int = 0, teardown: int = 0) -> None:
    """Update Test Case Data with specfiied duration(s) and recalculate total."""
    test: TestTab = TestTab.get(nodeid=nodeid)
    if not test:
        TestTab(nodeid=nodeid, setup=setup, call=call, teardown=teardown, total=setup + call + teardown)
    else:
        if test.setup < setup:
            test.setup = setup
        if test.call < call:
            test.call = call
        if test.teardown < teardown:
            test.teardown = teardown
        total = test.setup + test.call + test.teardown
        if test.total < total:
            test.total = total


@_init_db
@db_session
def get_total(nodeid: str) -> int:
    """Retrieve the total duration for specified nodeid. (0 if not found)."""
    test: TestTab = TestTab.get(nodeid=nodeid)
    if not test:
        return 0
    return test.total


@_init_db
@db_session
def get_all_totals() -> dict:
    """Retrieve all total durations for all nodeids."""
    tests: list[TestTab] = TestTab.select(lambda _: True)
    return {test.nodeid: test.total for test in tests}


@_init_db
@db_session
def get_bucket_total(bucket_id: str) -> int:
    """Retrieve the total for all test nodeid that start with bucket_id. (0 if not found)."""
    tests: TestTab = TestTab.select(lambda t: bucket_id in t.nodeid)

    return sum([test.total for test in tests])


@_init_db
@db_session
def get_stats(nodeid: str) -> dict:
    """Retrieve all stats for specified nodeid. (all zeroes if not found)."""
    test = TestTab.get(nodeid=nodeid)
    if not test:
        return {
            "setup": 0,
            "call": 0,
            "teardown": 0,
            "total": 0,
        }
    return {
        "setup": test.setup,
        "call": test.call,
        "teardown": test.teardown,
        "total": test.total,
    }
