"""Container for configuration of pytest_sort."""

from __future__ import annotations

import random
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pytest_sort import database

if TYPE_CHECKING:
    import pytest

modes = ["ordered", "reverse", "md5", "random", "fastest", "diffcov"]
bucket_types = ["session", "package", "module", "class", "function", "parent", "grandparent"]

legacy_modes = {
    "none": "ordered",
}
legacy_bucket_types = {
    "global": "session",
}


class SortConfig:
    """Statoc class for storing configuration of pytest_sort."""

    mode: str = "ordered"
    bucket: str = "parent"
    bucket_mode: str = "sort_mode"
    record: bool | None = None  # pragma: no mutate
    reset: bool = False
    report: bool = False

    seed = random.randint(0, 1_000_000)

    debug = False

    recorded_times: ClassVar[dict] = {}
    item_totals: ClassVar[dict] = {}
    item_sort_keys: ClassVar[dict] = {}
    item_bucket_id: ClassVar[dict] = {}
    bucket_sort_keys: ClassVar[dict] = {}
    cov_scores: ClassVar[dict] = {}

    @staticmethod
    def from_pytest(config: pytest.Config) -> None:
        """Extract pytest_sort settings from pytest's Config options and ini data."""
        SortConfig._mode_from_pytest(config)
        SortConfig._bucket_from_pytest(config)
        SortConfig._bucket_mode_from_pytest(config)
        SortConfig._record_from_pytest(config)

        SortConfig.reset = config.getoption("sort_reset_times", default=False)
        SortConfig.report = config.getoption("sort_report_times", default=False)

        SortConfig._seed_from_pytest(config)
        SortConfig._database_file_from_pytest(config)

        if config.getoption("sort_debug"):
            SortConfig.debug = True

    @staticmethod
    def _mode_from_pytest(config: pytest.Config) -> None:
        SortConfig.mode = config.getoption("sort_mode") or config.getini("sort_mode") or SortConfig.mode
        SortConfig.mode = legacy_modes.get(SortConfig.mode, SortConfig.mode)
        if SortConfig.mode not in modes:
            msg = f"Invalid Value for sort-mode='{SortConfig.mode}'"
            raise ValueError(msg)

    @staticmethod
    def _bucket_from_pytest(config: pytest.Config) -> None:
        SortConfig.bucket = config.getoption("sort_bucket") or config.getini("sort_bucket") or SortConfig.bucket
        SortConfig.bucket = legacy_bucket_types.get(SortConfig.bucket, SortConfig.bucket)
        if SortConfig.bucket not in bucket_types:
            msg = f"Invalid Value for sort-bucket='{SortConfig.bucket}'"
            raise ValueError(msg)

    @staticmethod
    def _bucket_mode_from_pytest(config: pytest.Config) -> None:
        SortConfig.bucket_mode = (
            config.getoption("sort_bucket_mode") or config.getini("sort_bucket_mode") or SortConfig.bucket_mode
        )
        if SortConfig.bucket_mode == "sort_mode":
            SortConfig.bucket_mode = SortConfig.mode
        SortConfig.bucket_mode = legacy_modes.get(SortConfig.bucket_mode, SortConfig.bucket_mode)
        if SortConfig.bucket_mode not in modes:
            msg = f"Invalid Value for sort-bucket-mode='{SortConfig.bucket_mode}'"
            raise ValueError(msg)

    @staticmethod
    def _record_from_pytest(config: pytest.Config) -> None:
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

    @staticmethod
    def _seed_from_pytest(config: pytest.Config) -> None:
        SortConfig.seed = config.getoption("sort_seed") or config.getini("sort_seed") or SortConfig.seed
        if not str(SortConfig.seed).isdigit():
            msg = f"Invalid seed value '{SortConfig.seed}' must be int"
            raise ValueError(msg)
        SortConfig.seed = int(str(SortConfig.seed))

    @staticmethod
    def _database_file_from_pytest(config: pytest.Config) -> None:
        database_file = config.getoption("sort_datafile") or config.getini("sort_datafile") or None
        if database_file:
            database.database_file = Path(database_file)

    @staticmethod
    def header_dict() -> dict:
        """Construct dict of pytest_sort configuration data for use in displaying header.

        Skips settings that are not currently in use.
        """
        config: dict[str, Any] = {
            "sort-mode": SortConfig.mode,
        }

        if SortConfig.mode not in ("ordered", "reverse") or SortConfig.bucket_mode != SortConfig.mode:
            config["sort-bucket"] = SortConfig.bucket

        if SortConfig.bucket_mode != SortConfig.mode:
            config["sort-bucket-mode"] = SortConfig.bucket_mode

        if SortConfig.mode == "random":
            config["sort-seed"] = SortConfig.seed

        if SortConfig.reset:
            config["sort-reset-times"] = True

        if SortConfig.record is not None:
            config["sort-record-times"] = SortConfig.record

        if SortConfig.report:
            config["sort-report-times"] = True

        if SortConfig.debug:
            config["sort-debug"] = True

        return config
