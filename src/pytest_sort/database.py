"""Manages datafile for pytest_sort plugin."""

from __future__ import annotations

import json
from pathlib import Path

database_file = Path.cwd() / ".pytest_sort_data"

_sort_data: dict = {}


def _load_data() -> None:
    global _sort_data
    if not _sort_data and database_file.exists():
        _sort_data = json.loads(database_file.read_text("utf-8"))


def _save_data() -> None:
    database_file.write_text(json.dumps(_sort_data, indent=4), "utf-8")


def clear_db() -> None:
    """Clear Saved Data."""
    global _sort_data
    _sort_data = {}
    _save_data()


def update_test_cases(recorded_times: dict) -> None:
    """Update Test Case Data with specfiied duration(s) and recalculate total(s)."""
    _load_data()

    for nodeid in recorded_times:
        node_data = _sort_data.get(nodeid, {})

        node_data["setup"] = node_data.get("setup", 0)
        node_data["call"] = node_data.get("call", 0)
        node_data["teardown"] = node_data.get("teardown", 0)

        setup = recorded_times[nodeid].get("setup", 0)
        if node_data["setup"] < setup:
            node_data["setup"] = setup

        call = recorded_times[nodeid].get("call", 0)
        if node_data["call"] < call:
            node_data["call"] = call

        teardown = recorded_times[nodeid].get("teardown", 0)
        if node_data["teardown"] < teardown:
            node_data["teardown"] = teardown

        node_data["total"] = node_data["setup"] + node_data["call"] + node_data["teardown"]

        _sort_data[nodeid] = node_data

    _save_data()


def get_all_totals() -> dict:
    """Retrieve all total durations for all nodeids."""
    _load_data()
    return {nodeid: _sort_data[nodeid]["total"] for nodeid in _sort_data}


def get_bucket_total(bucket_id: str) -> int:
    """Retrieve the total for all test nodeid that start with bucket_id. (0 if not found)."""
    _load_data()
    return sum([_sort_data[nodeid]["total"] for nodeid in _sort_data if nodeid.startswith(bucket_id)])


def get_stats(nodeid: str) -> dict:
    """Retrieve all stats for specified nodeid. (all zeroes if not found)."""
    _load_data()
    return _sort_data.get(
        nodeid,
        {
            "setup": 0,
            "call": 0,
            "teardown": 0,
            "total": 0,
        },
    )
