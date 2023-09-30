"""Core logic for pytest_sort plugin."""

from __future__ import annotations

import hashlib
import random
import sys
from functools import partial
from typing import TYPE_CHECKING, Any, Callable

import pytest
from _pytest import nodes as pytest_nodes

from pytest_sort.config import SortConfig
from pytest_sort.database import get_all_totals, get_stats
from pytest_sort.diffcov import get_test_scores

md5: Callable = hashlib.md5
if sys.version_info >= (3, 9):
    md5: Callable = partial(hashlib.md5, usedforsecurity=False)  # type: ignore[no-redef]


if TYPE_CHECKING:
    from _pytest.terminal import TerminalReporter


def create_bucket_id_from_node(node: pytest_nodes.Node | None) -> str:
    """Extract portion of nodeid needed for bucket key."""
    if isinstance(node, pytest.Package):
        return node.nodeid.replace("__init__.py", "")

    if isinstance(node, pytest_nodes.Node):
        return node.nodeid

    return ""


def create_bucket_id_for_package(node: pytest_nodes.Node | None) -> str:
    """Extract package name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package)):
        return create_bucket_id_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_id_for_package(node.parent)

    return ""


def create_bucket_id_for_module(node: pytest_nodes.Node | None) -> str:
    """Extract module name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package, pytest.Module)):
        return create_bucket_id_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_id_for_module(node.parent)

    return ""


def create_bucket_id_for_class(node: pytest_nodes.Node | None) -> str:
    """Extract class or module name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package, pytest.Module, pytest.Class)):
        return create_bucket_id_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_id_for_class(node.parent)

    return ""


create_bucket_id = {
    "session": lambda item: "",
    "package": create_bucket_id_for_package,
    "module": create_bucket_id_for_module,
    "class": create_bucket_id_for_class,
    "function": lambda item: item.nodeid,
    "parent": lambda item: create_bucket_id_from_node(item.parent),
    "grandparent": lambda item: create_bucket_id_from_node(item.parent.parent),
}

create_item_key = {
    "ordered": lambda item, idx, count: idx + 1,
    "reverse": lambda item, idx, count: count - idx,
    "md5": lambda item, idx, count: md5(item.nodeid.encode()).digest(),
    "random": lambda item, idx, count: random.random(),
    "fastest": lambda item, idx, count: SortConfig.item_totals.get(item.nodeid, 0),
    "diffcov": lambda item, idx, count: SortConfig.cov_scores.get(item.nodeid, 0),
}


def get_bucket_total(bucket_id: str) -> int:
    """Get all totals from nodes matching this bucket and return sum."""
    return sum([total for nodeid, total in SortConfig.item_totals.items() if nodeid.startswith(bucket_id)])


def get_bucket_score(bucket_id: str) -> int:
    """Get all scores from nodes matching this bucket and return min."""
    return min([score for nodeid, score in SortConfig.cov_scores.items() if nodeid.startswith(bucket_id)] + [0])


create_bucket_key = {
    "ordered": lambda bucket_id, idx, count: idx + 1,
    "reverse": lambda bucket_id, idx, count: count - idx,
    "md5": lambda bucket_id, idx, count: md5(bucket_id.encode()).digest(),
    "random": lambda bucket_id, idx, count: random.random(),
    "fastest": lambda bucket_id, idx, count: get_bucket_total(bucket_id),
    "diffcov": lambda bucket_id, idx, count: get_bucket_score(bucket_id),
}


def validate_order_marker(order_marker: pytest.Mark, node_id: str) -> Any:  # noqa: ANN401
    """Validate values from order marker.

    Returns sort_key
    """

    def mark_order_parse(item_sort_key: Any) -> Any:  # noqa: ANN401
        return item_sort_key

    try:
        return mark_order_parse(*order_marker.args, **order_marker.kwargs)
    except TypeError as e:
        msg = f"Incorrect arguments on marker 'order'. Target:{node_id}"
        raise TypeError(msg) from e


def validate_sort_marker(sort_marker: pytest.Mark, node_id: str) -> tuple:
    """Validate values from sort marker.

    Returns (mode, bucket)
    """

    def mark_sort_parse(mode: str, bucket: str = "self") -> tuple:
        return (mode, bucket)

    try:
        (mode, bucket_temp) = mark_sort_parse(*sort_marker.args, **sort_marker.kwargs)
    except TypeError as e:
        msg = f"Incorrect arguments on marker 'sort'. Target:{node_id}"
        raise TypeError(msg) from e

    if mode not in create_item_key:
        msg = f"Invalid Value for 'mode' on 'sort' marker. Value:{mode} Target:{node_id}"
        raise ValueError(msg)

    return (mode, bucket_temp)


def get_marker_settings(node: pytest_nodes.Node) -> tuple:
    """Retrieve and validate options on 'sort' and 'order' markers.

    Recursively calls with node.parent to get values from any level.

    Returns: (mode, bucket, bucket_id, bucket_sort_key, sort_key)
    """
    mode = None
    bucket = None
    bucket_id = None
    bucket_sort_key = None
    item_sort_key = None

    node_id = node.nodeid

    if node.parent:
        (mode, bucket, bucket_id, bucket_sort_key, item_sort_key) = get_marker_settings(node.parent)

    for order in node.iter_markers("order"):
        sort_key = validate_order_marker(order, node_id)
        if isinstance(node, pytest.Function):
            item_sort_key = sort_key
        else:
            bucket_sort_key = sort_key
            bucket_id = create_bucket_id_from_node(node)

    for sort in node.iter_markers("sort"):
        (mode, bucket_temp) = validate_sort_marker(sort, node_id)

        if bucket_temp == "self":
            bucket_id = create_bucket_id_from_node(node)
        elif bucket_temp in create_bucket_id:
            bucket = bucket_temp
            bucket_id = None
            bucket_sort_key = None
        else:
            msg = f"Invalid Value for 'bucket' on 'sort' marker: {bucket_temp}. Target: {node_id}"
            raise ValueError(msg)

    return (mode, bucket, bucket_id, bucket_sort_key, item_sort_key)


def create_sort_keys(item: pytest.Item, idx: int, count: int) -> None:
    """Create item and bucket sort keys.

    Store in SortConfig.item_sort_keys and SortConfig.bucket_sort_keys
    """
    (mode, bucket, bucket_id, bucket_sort_key, item_sort_key) = get_marker_settings(item)

    SortConfig.item_sort_keys[item.nodeid] = item_sort_key or create_item_key[mode or SortConfig.mode](item, idx, count)

    bucket_id = bucket_id or create_bucket_id[bucket or SortConfig.bucket](item)
    SortConfig.item_bucket_id[item.nodeid] = bucket_id

    bucket_key = bucket_sort_key or create_bucket_key[SortConfig.bucket_mode](bucket_id, idx, count)
    if bucket_id in SortConfig.bucket_sort_keys:
        SortConfig.bucket_sort_keys[bucket_id] = min(SortConfig.bucket_sort_keys[bucket_id], bucket_key)
    else:
        SortConfig.bucket_sort_keys[bucket_id] = bucket_key


def get_item_sort_key(item: pytest.Item) -> tuple:
    """Build Combined Sort Key for this Item using the Bucket Keys and Item Keys stored in SortConfig."""
    node_id = item.nodeid
    bucket_id = SortConfig.item_bucket_id[node_id]
    return (SortConfig.bucket_sort_keys[bucket_id], SortConfig.item_sort_keys[node_id])


def sort_items(items: list[pytest.Item]) -> None:
    """Reorder the items."""
    if SortConfig.mode == "random" or SortConfig.bucket_mode == "random":
        random.seed(SortConfig.seed)

    if SortConfig.mode == "diffcov" or SortConfig.bucket_mode == "diffcov":
        SortConfig.cov_scores = get_test_scores()

    if SortConfig.mode == "fastest" or SortConfig.bucket_mode == "fastest":
        SortConfig.item_totals = get_all_totals()

    for idx, item in enumerate(items):
        create_sort_keys(item, idx, len(items))

    items.sort(key=get_item_sort_key)

    if SortConfig.debug:
        print_test_case_order(items)


def print_recorded_times_report(terminal_reporter: TerminalReporter) -> None:
    """Print a summary report of maximum recorded times."""
    nodeids = list({rpt.nodeid for rpt in terminal_reporter.stats[""]})
    nodeids.sort()

    node_id_width = max([len(nodeid) for nodeid in nodeids]) + 3
    stat_width = 16

    print(
        f"\n*** {'pytest-sort maximum recorded times'.ljust(node_id_width)}"
        f"{'Nanoseconds'.center(stat_width*4 - 4)} ***",
    )
    print(
        f"{'Test Case'.ljust(node_id_width)} {'setup'.rjust(stat_width)} "
        f"{'call'.rjust(stat_width)} {'teardown'.rjust(stat_width)} {'total'.rjust(stat_width)}",
    )
    for nodeid in nodeids:
        stats = get_stats(nodeid)
        setup_ns = f"{stats['setup']:,}"
        call_ns = f"{stats['call']:,}"
        teardown_ns = f"{stats['teardown']:,}"
        total_ns = f"{stats['total']:,}"
        print(
            f"{nodeid.ljust(node_id_width)} {setup_ns.rjust(stat_width)} "
            f"{call_ns.rjust(stat_width)} {teardown_ns.rjust(stat_width)} {total_ns.rjust(stat_width)}",
        )


def print_test_case_order(items: list[pytest.Item]) -> None:
    """Print test items sort data: bucket_key, bucket_id, item_key, item_id."""
    print("\nTest Case Order:")
    print("(bucket_key, bucket_id, item_key, item_id)")
    for item in items:
        node_id = item.nodeid
        bucket_id = SortConfig.item_bucket_id[node_id]
        print((SortConfig.bucket_sort_keys[bucket_id], bucket_id, SortConfig.item_sort_keys[node_id], node_id))
