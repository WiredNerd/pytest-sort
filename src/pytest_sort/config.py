"""Container for configuration of pytest_sort."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pytest


class SortConfig:
    """Statoc class for storing configuration of pytest_sort."""

    mode: str = "none"
    bucket: str = "module"
    record: bool | None = False
    reset: bool = False
    report: bool = False

    seed = random.randint(0, 1_000_000)

    @staticmethod
    def from_pytest(config: pytest.Config) -> None:
        """Extract pytest_sort settings from pytest's Config options and ini data."""
        SortConfig.mode = config.getoption("sort_mode") or config.getini("sort_mode") or "none"
        SortConfig.bucket = config.getoption("sort_bucket") or config.getini("sort_bucket") or "module"

        if config.getoption("sort_no_record") and config.getoption("sort_record"):
            raise ValueError("Do not use both --sort-record-times and --sort-no-record-times")

        if config.getoption("sort_no_record"):
            SortConfig.record = False
        else:
            SortConfig.record = config.getoption("sort_record") or config.getini("sort_record_times")
        # getini returns [] when option not specified
        if not isinstance(SortConfig.record, bool):
            SortConfig.record = None
        if SortConfig.mode == "fastest" and SortConfig.record is None:
            SortConfig.record = True

        SortConfig.reset = config.getoption("sort_reset_times", default=False)
        SortConfig.report = config.getoption("sort_report_times", default=False)

        SortConfig.seed = config.getoption("sort_seed") or config.getini("sort_seed") or SortConfig.seed

    @staticmethod
    def header_dict() -> dict:
        """Construct dict of pytest_sort configuration data for use in displaying header.

        Skips settings that are not currently in use.
        """
        config: dict[str, Any] = {
            "sort-mode": SortConfig.mode,
        }

        if SortConfig.mode == "random":
            config["sort-seed"] = SortConfig.seed

        if SortConfig.mode != "none":
            config["sort-bucket"] = SortConfig.bucket

        if SortConfig.reset:
            config["sort-reset-times"] = True

        if SortConfig.record is not None:
            config["sort-record-times"] = SortConfig.record

        if SortConfig.report:
            config["sort-report-times"] = True

        return config
