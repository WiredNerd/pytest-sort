"""Pytest plugin code for pytest_sort."""

from __future__ import annotations

from typing import TYPE_CHECKING, Generator

import pytest

from pytest_sort.config import SortConfig
from pytest_sort.core import sort_items
from pytest_sort.database import clear_db, get_stats, update_test_case

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


def pytest_addoption(parser: pytest.Parser) -> None:
    """pytest_sort: Add command line and ini options to pytest."""
    group = parser.getgroup("pytest-sort")

    help_text = """
    none   = (default) pytest_sort will not modify order.
    md5    = Sort by md5 of test name.
    random = randomly sort tests.
    fastest = use recorded times to run fastest tests first.
    """
    choices = ["none", "random", "md5", "fastest"]
    group.addoption("--sort-mode", action="store", dest="sort_mode", choices=choices, help=help_text)
    parser.addini("sort_mode", help=str(choices))

    help_text = "Sort test order within specified test buckets. (default: module)"
    choices = ["global", "package", "module", "class", "parent", "grandparent"]
    group.addoption("--sort-bucket", action="store", dest="sort_bucket", choices=choices, help=help_text)
    parser.addini("sort_bucket", help=str(choices))

    help_text = "Random Seed to use with random mode."
    group.addoption("--sort-seed", action="store", dest="sort_seed", help=help_text)
    parser.addini("sort_seed", help=help_text)

    help_text = "Records runtimes.  Activated by default when sort-mode=fastest"
    group.addoption("--sort-record-times", action="store_true", dest="sort_record", help=help_text)
    group.addoption("--sort-no-record-times", action="store_true", dest="sort_no_record", help=help_text)
    parser.addini("sort_record_times", help=help_text, type="bool")

    help_text = "Clear the recorded runtimes before sorting."
    group.addoption("--sort-reset-times", action="store_true", dest="sort_reset_times", help=help_text)

    help_text = "At end of report current times."
    group.addoption("--sort-report-times", action="store_true", dest="sort_report_times", help=help_text)


def pytest_configure(config: pytest.Config) -> None:
    """pytest_sort: Add markers to pytest."""
    config.addinivalue_line("markers", "sort(bucket): Override pytest-sort Options.")


def pytest_report_header(config: pytest.Config) -> str:
    """pytest_sort: Build Header for pytest to display."""
    SortConfig.from_pytest(config)

    header = "pytest-sort:"

    for key, value in SortConfig.header_dict().items():
        header += f"\n  {key}: {value}"

    return header


def pytest_collection_modifyitems(
    session: pytest.Session,  # noqa: ARG001
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """pytest_sort: Modify item order."""
    SortConfig.from_pytest(config)

    if SortConfig.reset:
        clear_db()

    if SortConfig.mode != "none":
        sort_items(items)


recorded_times: dict = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
    """pytest_sort: Record test runtimes in memory."""
    if SortConfig.record and call.when in ("setup", "call", "teardown"):
        global recorded_times  # noqa: PLW0602

        duration = int(call.duration * 1_000_000_000)  # convert to ns

        if item.nodeid not in recorded_times:
            recorded_times[item.nodeid] = {}

        recorded_times[item.nodeid][call.when] = duration

    yield


def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: int,  # noqa: ARG001
    config: pytest.Config,  # noqa: ARG001
) -> None:
    """pytest_sort: Store recorded runtimes in database."""
    global recorded_times  # noqa: PLW0602

    for nodeid in recorded_times:
        update_test_case(nodeid, **recorded_times[nodeid])

    if SortConfig.report:
        nodeids = list({rpt.nodeid for rpt in terminalreporter.stats[""]})
        nodeids.sort()

        node_id_width = max([len(nodeid) for nodeid in nodeids]) + 3
        stat_width = 16

        print(  # noqa: T201
            f"\n*** {'pytest-sort maximum recorded times'.ljust(node_id_width)}"
            f"{'Nanoseconds'.center(stat_width*4 - 4)} ***",
        )
        print(  # noqa: T201
            f"{'Test Case'.ljust(node_id_width)} {'setup'.rjust(stat_width)} "
            f"{'call'.rjust(stat_width)} {'teardown'.rjust(stat_width)} {'total'.rjust(stat_width)}",
        )
        for nodeid in nodeids:
            stats = get_stats(nodeid)
            setup_ns = f"{stats['setup']:,}"
            call_ns = f"{stats['call']:,}"
            teardown_ns = f"{stats['teardown']:,}"
            total_ns = f"{stats['total']:,}"
            print(  # noqa: T201
                f"{nodeid.ljust(node_id_width)} {setup_ns.rjust(stat_width)} "
                f"{call_ns.rjust(stat_width)} {teardown_ns.rjust(stat_width)} {total_ns.rjust(stat_width)}",
            )

    for key in SortConfig.sort_keys:
        print(key)
