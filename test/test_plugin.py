import argparse
import importlib
from unittest import mock

import pytest

from pytest_sort import plugin
from pytest_sort.config import bucket_types, modes


def test_plugin():
    importlib.reload(plugin)


class TestConfig:
    def test_pytest_addoption(self):
        parser = mock.MagicMock()
        group = parser.getgroup.return_value

        plugin.pytest_addoption(parser)

        parser.getgroup.assert_called_with("pytest-sort")

        group.addoption.assert_any_call("--sort-mode", action="store", dest="sort_mode", help=str(modes))
        group.addoption.assert_any_call("--sort_mode", action="store", dest="sort_mode", help=argparse.SUPPRESS)
        parser.addini.assert_any_call("sort_mode", help=str(modes))

        group.addoption.assert_any_call("--sort-bucket", action="store", dest="sort_bucket", help=str(bucket_types))
        group.addoption.assert_any_call("--sort_bucket", action="store", dest="sort_bucket", help=argparse.SUPPRESS)
        parser.addini.assert_any_call("sort_bucket", help=str(bucket_types))

        choices = ["sort_mode"]
        choices.extend(modes)
        group.addoption.assert_any_call(
            "--sort-bucket-mode", action="store", dest="sort_bucket_mode", help=str(choices)
        )
        group.addoption.assert_any_call(
            "--sort_bucket_mode", action="store", dest="sort_bucket_mode", help=argparse.SUPPRESS
        )
        parser.addini.assert_any_call("sort_bucket_mode", help=str(choices))

        help_text = "Random Seed to use with random mode."
        group.addoption.assert_any_call("--sort-seed", action="store", dest="sort_seed", help=help_text)
        group.addoption.assert_any_call("--sort_seed", action="store", dest="sort_seed", help=argparse.SUPPRESS)
        parser.addini.assert_any_call("sort_seed", help=help_text)

        help_text = "Records runtimes. Activated by default when sort-mode=fastest"
        group.addoption.assert_any_call("--sort-record-times", action="store_true", dest="sort_record", help=help_text)
        group.addoption.assert_any_call(
            "--sort_record_times", action="store_true", dest="sort_record", help=argparse.SUPPRESS
        )
        group.addoption.assert_any_call(
            "--sort-no-record-times", action="store_true", dest="sort_no_record", help=help_text
        )
        group.addoption.assert_any_call(
            "--sort_no_record_times", action="store_true", dest="sort_no_record", help=argparse.SUPPRESS
        )
        parser.addini.assert_any_call("sort_record_times", help=help_text, type="bool")

        help_text = "Clear the recorded runtimes before sorting."
        group.addoption.assert_any_call(
            "--sort-reset-times", action="store_true", dest="sort_reset_times", help=help_text
        )
        group.addoption.assert_any_call(
            "--sort_reset_times", action="store_true", dest="sort_reset_times", help=argparse.SUPPRESS
        )

        help_text = "At end of report current times."
        group.addoption.assert_any_call(
            "--sort-report-times", action="store_true", dest="sort_report_times", help=help_text
        )
        group.addoption.assert_any_call(
            "--sort_report_times", action="store_true", dest="sort_report_times", help=argparse.SUPPRESS
        )

        help_text = "Location to store pytest-sort data. (default: ./.pytest_sort)"
        group.addoption.assert_any_call("--sort-datafile", action="store", dest="sort_datafile", help=help_text)
        group.addoption.assert_any_call("--sort_datafile", action="store", dest="sort_datafile", help=argparse.SUPPRESS)
        parser.addini.assert_any_call("sort_datafile", help=help_text)

        group.addoption.assert_any_call("--sort-debug", action="store_true", dest="sort_debug", help=argparse.SUPPRESS)
        group.addoption.assert_any_call("--sort_debug", action="store_true", dest="sort_debug", help=argparse.SUPPRESS)

    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_configure(self, SortConfig):
        config = mock.MagicMock()

        plugin.pytest_configure(config)

        config.addinivalue_line.assert_has_calls(
            [
                mock.call("markers", "sort(mode,bucket): Override pytest-sort Options."),
                mock.call(
                    "markers", "order(item_sort_key): Always use specified Sort Key for this test item or bucket."
                ),
            ]
        )

        SortConfig.from_pytest.assert_called_with(config)

    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_report_header(self, SortConfig):
        config = mock.MagicMock()
        SortConfig.header_dict.return_value = {
            "sort-mode": "random",
            "sort-bucket": "module",
        }

        header = plugin.pytest_report_header(config)

        assert header == "pytest-sort:\n  sort-mode: random\n  sort-bucket: module"


class TestExecute:
    @mock.patch("pytest_sort.plugin.sort_items")
    @mock.patch("pytest_sort.plugin.clear_db")
    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_collection_modifyitems(self, SortConfig, clear_db, sort_items):
        session = mock.MagicMock()
        config = mock.MagicMock()
        items = mock.MagicMock()

        SortConfig.reset = False

        plugin.pytest_collection_modifyitems(session, config, items)
        clear_db.assert_not_called()
        sort_items.assert_called_with(items)

    @mock.patch("pytest_sort.plugin.sort_items")
    @mock.patch("pytest_sort.plugin.clear_db")
    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_collection_modifyitems_reset(self, SortConfig, clear_db, sort_items):
        session = mock.MagicMock()
        config = mock.MagicMock()
        items = mock.MagicMock()

        SortConfig.reset = True

        plugin.pytest_collection_modifyitems(session, config, items)
        clear_db.assert_called()
        sort_items.assert_called_with(items)

    @pytest.mark.parametrize(
        "record,recorded_times,when,out_recorded_times",
        [
            (True, {}, "setup", {"test_item_1": {"setup": 1_123_456_789}}),
            (True, {}, "call", {"test_item_1": {"call": 1_123_456_789}}),
            (True, {}, "teardown", {"test_item_1": {"teardown": 1_123_456_789}}),
            (True, {}, "collect", {}),
            (True, {"test_item_1": {"setup": 5}}, "call", {"test_item_1": {"setup": 5, "call": 1_123_456_789}}),
            (False, {}, "setup", {}),
        ],
    )
    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_runtest_makereport(self, SortConfig, record, recorded_times, when, out_recorded_times):
        SortConfig.record = record
        SortConfig.recorded_times = recorded_times

        item = mock.MagicMock(nodeid="test_item_1")
        call = mock.MagicMock(when=when, duration=1.123_456_789)

        for i in plugin.pytest_runtest_makereport(item, call):
            assert i is None

        assert SortConfig.recorded_times == out_recorded_times

    @mock.patch("pytest_sort.plugin.print_recorded_times_report")
    @mock.patch("pytest_sort.plugin.update_test_cases")
    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_terminal_summary(self, SortConfig, update_test_cases, print_recorded_times_report):
        SortConfig.recorded_times = {
            "test_item_1": {"setup": 1},
            "test_item_2": {"setup": 2},
        }
        terminalreporter = mock.MagicMock()
        exitstatus = mock.MagicMock()
        config = mock.MagicMock()

        SortConfig.report = True

        plugin.pytest_terminal_summary(terminalreporter, exitstatus, config)

        update_test_cases.assert_called_with(SortConfig.recorded_times)
        print_recorded_times_report.assert_called_with(terminalreporter)

    @mock.patch("pytest_sort.plugin.print_recorded_times_report")
    @mock.patch("pytest_sort.plugin.update_test_cases")
    @mock.patch("pytest_sort.plugin.SortConfig")
    def test_pytest_terminal_summary_false(self, SortConfig, update_test_cases, print_recorded_times_report):
        SortConfig.recorded_times = {}
        terminalreporter = mock.MagicMock()
        exitstatus = mock.MagicMock()
        config = mock.MagicMock()

        SortConfig.report = False

        plugin.pytest_terminal_summary(terminalreporter, exitstatus, config)

        update_test_cases.assert_not_called()
        print_recorded_times_report.assert_not_called()
