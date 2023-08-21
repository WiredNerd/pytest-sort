"""Core logic for pytest_sort plugin."""

from __future__ import annotations

import hashlib
import os
import random
import sys
from functools import partial
from typing import TYPE_CHECKING, Callable

import pytest
from _pytest import nodes as pytest_nodes

from pytest_sort.config import SortConfig
from pytest_sort.database import get_bucket_total, get_total

md5: Callable = hashlib.md5
if sys.version_info >= (3, 9):
    md5: Callable = partial(hashlib.md5, usedforsecurity=False)  # type: ignore[no-redef]


def create_bucket_key_from_node(node: pytest_nodes.Node) -> str:
    """Extract portion of nodeid needed for bucket key."""
    if isinstance(node, pytest.Package):
        return node.nodeid.replace("__init__.py", "")
    return node.nodeid


def create_bucket_key_for_package(node: pytest_nodes.Node) -> str:
    """Extract package name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package)):
        return create_bucket_key_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_key_for_package(node.parent)

    return ""


def create_bucket_key_for_module(node: pytest_nodes.Node) -> str:
    """Extract module name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package, pytest.Module)):
        return create_bucket_key_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_key_for_module(node.parent)

    return ""


def create_bucket_key_for_class(node: pytest_nodes.Node) -> str:
    """Extract class or module name from pytest item."""
    if isinstance(node, (pytest.Session, pytest.Package, pytest.Module, pytest.Class)):
        return create_bucket_key_from_node(node)

    if isinstance(node, (pytest_nodes.Node)):
        return create_bucket_key_for_class(node.parent)

    return ""


create_bucket_key = {
    "global": lambda item: "",  # noqa: ARG005
    "package": create_bucket_key_for_package,
    "module": create_bucket_key_for_module,
    "class": create_bucket_key_for_class,
    "parent": lambda item: create_bucket_key_from_node(item.parent),
    "grandparent": lambda item: create_bucket_key_from_node(item.parent.parent),
}

create_item_key = {
    "md5": lambda item: md5(item.nodeid.encode()).digest(),
    "none": lambda item: (_ for _ in ()).throw(ValueError("Should not generate key for mode=none")),  # noqa: ARG005
    "random": lambda item: random.random(),  # noqa: ARG005
    "fastest": lambda item: get_total(item.nodeid),
}


def get_bucket_priority(item: pytest.Item, bucket_key: str) -> int:
    """Get bucket priority for item."""
    if bucket_key in SortConfig.bucket_priorities:
        return SortConfig.bucket_priorities[bucket_key]

    if SortConfig.mode == 'fastest':
        SortConfig.bucket_priorities[bucket_key] = get_bucket_total(bucket_key)
        return SortConfig.bucket_priorities[bucket_key]

    return SortConfig.default_priority


def get_item_priority(item: pytest.Item) -> int:
    """Get order priority for item."""
    return SortConfig.default_priority


def create_sort_key(item: pytest.Item) -> tuple:
    """Create Sort Key for Item.

    Returns tuple as (bucket_priority, bucket_key, item_priority, item_key, item.nodeid)
    """
    bucket_key = create_bucket_key[SortConfig.bucket](item)
    bucket_priority = get_bucket_priority(item, bucket_key)

    item_key = create_item_key[SortConfig.mode](item)
    item_priority = get_item_priority(item)

    sort_key = (bucket_priority, bucket_key, item_priority, item_key, item.nodeid)
    SortConfig.sort_keys.append(sort_key)

    return sort_key


def sort_items(items: list[pytest.Item]) -> None:
    """Reorder the items."""
    if SortConfig.mode == "random":
        random.seed(SortConfig.seed)

    items.sort(key=create_sort_key)
