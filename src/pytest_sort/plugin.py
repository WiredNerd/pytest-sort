"""Pytest plugin code for pytest_sort."""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Generator

import pytest

from pytest_sort.config import SortConfig, bucket_types, modes
from pytest_sort.core import print_recorded_times_report, sort_items
from pytest_sort.database import clear_db, update_test_case

if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


def pytest_addoption(parser: pytest.Parser) -> None:
    """pytest_sort: Add command line and ini options to pytest."""
    group = parser.getgroup("pytest-sort")

    group.addoption("--sort-mode", action="store", dest="sort_mode", choices=modes)
    parser.addini("sort_mode", help=str(modes))

    group.addoption("--sort-bucket", action="store", dest="sort_bucket", choices=bucket_types)
    parser.addini("sort_bucket", help=str(bucket_types))

    choices = ["sort_mode"]
    choices.extend(modes)
    group.addoption("--sort-bucket-mode", action="store", dest="sort_bucket_mode", choices=choices)
    parser.addini("sort_bucket_mode", help=str(choices))

    help_text = "Random Seed to use with random mode."
    group.addoption("--sort-seed", action="store", dest="sort_seed", help=help_text)
    parser.addini("sort_seed", help=help_text)

    help_text = "Records runtimes. Activated by default when sort-mode=fastest"
    group.addoption("--sort-record-times", action="store_true", dest="sort_record", help=help_text)
    group.addoption("--sort-no-record-times", action="store_true", dest="sort_no_record", help=help_text)
    parser.addini("sort_record_times", help=help_text, type="bool")

    help_text = "Clear the recorded runtimes before sorting."
    group.addoption("--sort-reset-times", action="store_true", dest="sort_reset_times", help=help_text)

    help_text = "At end of report current times."
    group.addoption("--sort-report-times", action="store_true", dest="sort_report_times", help=help_text)

    help_text = "Location to store pytest-sort data. (default: ./.pytest_sort)"
    group.addoption("--sort-datafile", action="store", dest="sort_datafile", help=help_text)
    parser.addini("sort_datafile", help=help_text)

    group.addoption("--sort-debug", action="store_true", dest="sort_debug", help=argparse.SUPPRESS)


def pytest_configure(config: pytest.Config) -> None:
    """pytest_sort: Add markers to pytest."""
    config.addinivalue_line(
        "markers",
        "sort(mode,bucket): Override pytest-sort Options.",
    )

    config.addinivalue_line(
        "markers",
        "order(item_sort_key): Always use specified Sort Key for this test item.",
    )
    SortConfig.from_pytest(config)


def pytest_report_header(config: pytest.Config) -> str:  # noqa: ARG001
    """pytest_sort: Build Header for pytest to display."""
    header = "pytest-sort:"

    for key, value in SortConfig.header_dict().items():
        header += f"\n  {key}: {value}"

    return header


def pytest_collection_modifyitems(
    session: pytest.Session,  # noqa: ARG001
    config: pytest.Config, # noqa: ARG001
    items: list[pytest.Item],
) -> None:
    """pytest_sort: Modify item order."""
    if SortConfig.reset:
        clear_db()

    sort_items(items)


@pytest.hookimpl(hookwrapper=True)  # pragma: no mutate
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> Generator:
    """pytest_sort: Record test runtimes in memory."""
    if SortConfig.record and call.when in ("setup", "call", "teardown"):
        duration = int(call.duration * 1_000_000_000)  # convert to ns

        if item.nodeid not in SortConfig.recorded_times:
            SortConfig.recorded_times[item.nodeid] = {}

        SortConfig.recorded_times[item.nodeid][call.when] = duration

    yield


def pytest_terminal_summary(
    terminalreporter: TerminalReporter,
    exitstatus: int,  # noqa: ARG001
    config: pytest.Config,  # noqa: ARG001
) -> None:
    """pytest_sort: Store recorded runtimes in database."""
    for nodeid in SortConfig.recorded_times:
        update_test_case(nodeid, **SortConfig.recorded_times[nodeid])

    if SortConfig.report:
        print_recorded_times_report(terminalreporter)
