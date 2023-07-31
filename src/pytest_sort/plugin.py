import hashlib
import os
import random
import sys
from collections import OrderedDict
from functools import partial
from typing import List

import pytest
from _pytest.terminal import TerminalReporter
from pytest import CallInfo, Config, Item, Parser, Session

from pytest_sort.config import SortConfig
from pytest_sort.database import clear_db, get_total, update_test_case

md5 = hashlib.md5
if sys.version_info >= (3, 9):
    md5: hashlib.md5 = partial(hashlib.md5, usedforsecurity=False)


def create_bucket_key_for_package(item: Item):
    if hasattr(item, "module"):
        return item.module.__package__
    return os.path.split(item.location[0])[0]


def create_bucket_key_for_class(item: Item):
    if hasattr(item, "module"):
        if hasattr(item, "cls") and item.cls:
            return item.module.__name__, item.cls.__name__
        return item.module.__name__
    return item.location[0]


create_bucket_key = {
    "global": lambda item: None,
    "package": create_bucket_key_for_package,
    "module": lambda item: item.location[0],
    "class": create_bucket_key_for_class,
    "parent": lambda item: item.parent,
    "grandparent": lambda item: item.parent.parent,
}

create_item_key = {
    "md5": lambda item: md5(item.nodeid.encode()).digest(),
    "none": lambda item: (_ for _ in ()).throw(ValueError("Should not generate key for mode=none")),
    "random": lambda item: random.random(),
    "fastest": lambda item: get_total(item.nodeid),
}


def pytest_addoption(parser: Parser):
    group = parser.getgroup("pytest-sort")
    group.addoption(
        '--sort-bucket',
        action='store',
        dest='sort_bucket',
        default="module",
        choices=create_bucket_key.keys(),
        help='Sort test order within specified test buckets. (default: module)',
    )
    group.addoption(
        "--sort-mode",
        action="store",
        dest="sort_mode",
        default="none",
        choices=create_item_key.keys(),
        help='''
        none   = (default) pytest_sort will not modify order.
        md5    = Sort by md5 of test name.
        random = randomly sort tests.
        fastest = use recorded times to run fastest tests first.
        ''',
    )
    group.addoption(
        "--sort-record-times",
        action="store_true",
        dest="sort_record",
        help="Records runtimes.  Activated by default when sort-mode=fastest",
    )
    group.addoption(
        "--sort-reset-times",
        action="store_true",
        dest="sort_reset_times",
        help="Clear the recorded runtimes before sorting.",
    )


def pytest_report_header(config: Config):
    SortConfig.from_pytest(config)

    header = "pytest-sort:"

    for key, value in SortConfig.dict().items():
        header += f"\n  {key}: {value}"

    return header


def pytest_collection_modifyitems(session: Session, config: Config, items: List[Item]):
    SortConfig.from_pytest(config)

    if SortConfig.reset:
        clear_db()

    if not SortConfig.mode == 'none':
        _sort(items)


def _sort(items: List[Item]):
    buckets: OrderedDict = OrderedDict()

    for item in items:
        bucket_key = create_bucket_key[SortConfig.bucket](item)
        if bucket_key not in buckets:
            buckets[bucket_key] = []
        buckets[bucket_key].append(item)

    for bucket_key in buckets.keys():
        buckets[bucket_key].sort(key=create_item_key[SortConfig.mode])

    items[:] = [item for bucket_key in buckets.keys() for item in buckets[bucket_key]]


recorded_times = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo):
    global recorded_times

    if SortConfig.record and call.when in ('setup', 'call', 'teardown'):
        duration = int(call.duration * 1_000_000_000)  # convert to ns

        if item.nodeid not in recorded_times:
            recorded_times[item.nodeid] = {}

        recorded_times[item.nodeid][call.when] = duration

    yield


def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: int, config: Config):
    global recorded_times

    for nodeid in recorded_times:
        update_test_case(nodeid, **recorded_times[nodeid])
