import hashlib
import importlib
import sys
from functools import partial
from typing import Callable
from unittest import mock

import pytest
from _pytest import nodes as pytest_nodes

from pytest_sort import config, core

md5: Callable = hashlib.md5
if sys.version_info >= (3, 9):
    md5: Callable = partial(hashlib.md5, usedforsecurity=False)  # type: ignore[no-redef]


@pytest.fixture
def mock_objects():
    session = mock.MagicMock(spec=pytest.Session)
    session.parent = None
    session.nodeid = "session"
    session.iter_markers.return_value = []

    package = mock.MagicMock(spec=pytest.Package)
    package.parent = session
    package.nodeid = "tests/core/__init__.py"
    package.iter_markers.return_value = []

    module = mock.MagicMock(spec=pytest.Module)
    module.parent = package
    module.nodeid = "tests/core/test_core.py"
    module.iter_markers.return_value = []

    cls = mock.MagicMock(spec=pytest.Class)
    cls.parent = module
    cls.nodeid = "tests/core/test_core.py::TestCoreStuff"
    cls.iter_markers.return_value = []

    func = mock.MagicMock(spec=pytest.Function)
    func.parent = cls
    func.nodeid = "tests/core/test_core.py::TestCoreStuff::test_init"
    func.iter_markers.return_value = []

    return (session, package, module, cls, func)


class TestCreateBucketIdForNode:
    @pytest.mark.parametrize(
        "type,nodeid,bucket_id",
        [
            (pytest.Package, "test/__init__.py", "test/"),
            (pytest.Package, "tests", "tests"),
            (pytest_nodes.Node, "test/__init__.py", "test/__init__.py"),
            (pytest_nodes.Node, "tests", "tests"),
            (pytest.Config, "tests", ""),
        ],
    )
    def test_create_bucket_id_from_node(self, type, nodeid, bucket_id):
        node = mock.MagicMock(spec=type)

        node.nodeid = nodeid
        assert core.create_bucket_id_from_node(node) == bucket_id

    def test_create_bucket_id_for_package(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        assert core.create_bucket_id_for_package(session) == "session"
        assert core.create_bucket_id_for_package(package) == "tests/core/"
        assert core.create_bucket_id_for_package(module) == "tests/core/"
        assert core.create_bucket_id_for_package(cls) == "tests/core/"
        assert core.create_bucket_id_for_package(func) == "tests/core/"

        module.parent = None
        assert core.create_bucket_id_for_package(module) == ""

    def test_create_bucket_id_for_module(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        assert core.create_bucket_id_for_module(session) == "session"
        assert core.create_bucket_id_for_module(package) == "tests/core/"
        assert core.create_bucket_id_for_module(module) == "tests/core/test_core.py"
        assert core.create_bucket_id_for_module(cls) == "tests/core/test_core.py"
        assert core.create_bucket_id_for_module(func) == "tests/core/test_core.py"

        cls.parent = None
        assert core.create_bucket_id_for_package(cls) == ""

    def test_create_bucket_id_for_class(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        assert core.create_bucket_id_for_class(session) == "session"
        assert core.create_bucket_id_for_class(package) == "tests/core/"
        assert core.create_bucket_id_for_class(module) == "tests/core/test_core.py"
        assert core.create_bucket_id_for_class(cls) == "tests/core/test_core.py::TestCoreStuff"
        assert core.create_bucket_id_for_class(func) == "tests/core/test_core.py::TestCoreStuff"

        func.parent = None
        assert core.create_bucket_id_for_package(func) == ""


class TestCreateBucketId:
    def test_create_bucket_id(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        core.create_bucket_id["session"](func) == ""
        core.create_bucket_id["package"](func) == "tests/core/"
        core.create_bucket_id["module"](func) == "tests/core/test_core.py"
        core.create_bucket_id["class"](func) == "tests/core/test_core.py::TestCoreStuff"
        core.create_bucket_id["parent"](func) == "tests/core/test_core.py::TestCoreStuff"
        core.create_bucket_id["grandparent"](func) == "tests/core/test_core.py"

    def test_create_item_key(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        assert core.create_item_key["ordered"](func, 5, 20) == 6
        assert core.create_item_key["reverse"](func, 5, 20) == 15

        md5_value = md5("tests/core/test_core.py::TestCoreStuff::test_init".encode()).digest()
        assert core.create_item_key["md5"](func, 5, 20) == md5_value

        assert 0 <= core.create_item_key["random"](func, 5, 20) < 1

        core.SortConfig.item_totals = {func.nodeid: 123}
        assert core.create_item_key["fastest"](func, 5, 20) == 123

    def test_create_bucket_key(self):
        assert core.create_bucket_key["ordered"]("tests", 5, 20) == 6
        assert core.create_bucket_key["reverse"]("tests", 5, 20) == 15

        md5_value = md5("tests".encode()).digest()
        assert core.create_bucket_key["md5"]("tests", 5, 20) == md5_value

        assert 0 <= core.create_bucket_key["random"]("tests", 5, 20) < 1

        core.SortConfig.item_totals = {
            "tests/core.py": 100,
            "tests/other/core.py": 23,
            "test/tests/core.py": 1,
        }

        assert core.create_bucket_key["fastest"]("tests", 5, 20) == 123


class TestValidateMarker:
    @pytest.mark.parametrize(
        "args,kwargs,key",
        [
            ([1234], {}, 1234),
            ([], {"item_sort_key": 1234}, 1234),
        ],
    )
    def test_validate_order_marker(self, args, kwargs, key):
        order_marker = mock.MagicMock()
        order_marker.args = args
        order_marker.kwargs = kwargs

        assert core.validate_order_marker(order_marker, "testnodeid") == key

    def test_validate_order_marker_error(self):
        order_marker = mock.MagicMock()
        order_marker.args = []
        order_marker.kwargs = {}

        with pytest.raises(TypeError, match="Incorrect arguments on marker 'order'. Target:testnodeid") as type_error:
            core.validate_order_marker(order_marker, "testnodeid")

        assert type(type_error.value.__cause__) == TypeError

    @pytest.mark.parametrize(
        "args,kwargs,key",
        [
            (["ordered", "parent"], {}, ("ordered", "parent")),
            (["ordered"], {"bucket": "parent"}, ("ordered", "parent")),
            ([], {"mode": "ordered", "bucket": "parent"}, ("ordered", "parent")),
            (["ordered"], {}, ("ordered", "self")),
        ],
    )
    def test_validate_sort_marker(self, args, kwargs, key):
        sort_marker = mock.MagicMock()
        sort_marker.args = args
        sort_marker.kwargs = kwargs

        assert core.validate_sort_marker(sort_marker, "testnodeid") == key

    def test_validate_sort_marker_type_error(self):
        sort_marker = mock.MagicMock()
        sort_marker.args = []
        sort_marker.kwargs = {}

        with pytest.raises(TypeError, match="Incorrect arguments on marker 'sort'. Target:testnodeid") as type_error:
            core.validate_sort_marker(sort_marker, "testnodeid")

        assert type(type_error.value.__cause__) == TypeError

    def test_validate_sort_marker_value_error(self):
        sort_marker = mock.MagicMock()
        sort_marker.args = ["invalid"]
        sort_marker.kwargs = {}

        with pytest.raises(
            ValueError, match="Invalid Value for 'mode' on 'sort' marker. Value:invalid Target:testnodeid"
        ) as type_error:
            core.validate_sort_marker(sort_marker, "testnodeid")

        assert not type_error.value.__cause__


class TestMarkerSettings:
    def test_geet_marker_settings_parent(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        order_1 = mock.MagicMock()
        order_1.args = [1]
        order_1.kwargs = {}

        order_10 = mock.MagicMock()
        order_10.args = [1]
        order_10.kwargs = {}

        sort_random = mock.MagicMock()
        sort_random.args = ["random"]
        sort_random.kwargs = {}

        sort_ordered = mock.MagicMock()
        sort_ordered.args = ["ordered", "parent"]
        sort_ordered.kwargs = {}

        module.iter_markers.side_effect = [[], [sort_random]]
        cls.iter_markers.side_effect = [[order_10], [sort_ordered]]
        func.iter_markers.side_effect = [[order_1], []]

        assert core.get_marker_settings(func) == ("ordered", "parent", None, 1)

    def test_geet_marker_settings_self(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        order_1 = mock.MagicMock()
        order_1.args = [1]
        order_1.kwargs = {}

        order_10 = mock.MagicMock()
        order_10.args = [1]
        order_10.kwargs = {}

        sort_random = mock.MagicMock()
        sort_random.args = ["random", "parent"]
        sort_random.kwargs = {}

        sort_ordered = mock.MagicMock()
        sort_ordered.args = ["ordered"]
        sort_ordered.kwargs = {}

        module.iter_markers.side_effect = [[], [sort_random]]
        cls.iter_markers.side_effect = [[order_10], [sort_ordered]]
        func.iter_markers.side_effect = [[order_1], []]

        assert core.get_marker_settings(func) == ("ordered", "parent", cls.nodeid, 1)

    def test_get_marker_settings_no_markers(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        assert core.get_marker_settings(func) == (None, None, None, None)

    def test_geet_marker_settings_error(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        sort_random = mock.MagicMock()
        sort_random.args = ["random", "hello"]
        sort_random.kwargs = {}

        module.iter_markers.side_effect = [[], [sort_random]]

        with pytest.raises(
            ValueError, match=f"Invalid Value for 'bucket' on 'sort' marker: hello. Target: {module.nodeid}"
        ):
            core.get_marker_settings(func)


class TestCreateSortKey:
    @pytest.fixture(autouse=True)
    def reset(self):
        importlib.reload(config)
        importlib.reload(core)
        yield

    @pytest.fixture
    def get_marker_settings(self):
        with mock.patch("pytest_sort.core.get_marker_settings") as get_marker_settings:
            yield get_marker_settings

    def test_marker_bucketid_sortkey(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, "test/core", 1234)
        config.SortConfig.bucket_mode = "ordered"
        (session, package, module, cls, func) = mock_objects

        core.create_sort_keys(func, 6, 60)

        get_marker_settings.assert_called_with(func)

        assert core.SortConfig.item_sort_keys == {func.nodeid: 1234}
        assert core.SortConfig.item_bucket_id == {func.nodeid: "test/core"}
        assert core.SortConfig.bucket_sort_keys == {"test/core": 7}

    def test_marker_mode_bucket(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = ("reverse", "class", None, None)
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket_mode = "ordered"
        (session, package, module, cls, func) = mock_objects

        core.create_sort_keys(func, 6, 60)

        get_marker_settings.assert_called_with(func)

        assert config.SortConfig.item_sort_keys == {func.nodeid: 54}
        assert config.SortConfig.item_bucket_id == {func.nodeid: cls.nodeid}
        assert config.SortConfig.bucket_sort_keys == {cls.nodeid: 7}

    def test_mode_ordered_reverse(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, None, None)
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket = "module"
        config.SortConfig.bucket_mode = "reverse"
        (session, package, module, cls, func) = mock_objects

        core.create_sort_keys(func, 6, 60)

        assert config.SortConfig.item_sort_keys == {func.nodeid: 7}
        assert config.SortConfig.item_bucket_id == {func.nodeid: module.nodeid}
        assert config.SortConfig.bucket_sort_keys == {module.nodeid: 54}

    def test_mode_reverse_ordered(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, None, None)
        config.SortConfig.mode = "reverse"
        config.SortConfig.bucket = "module"
        config.SortConfig.bucket_mode = "ordered"
        (session, package, module, cls, func) = mock_objects

        core.create_sort_keys(func, 6, 60)

        assert config.SortConfig.item_sort_keys == {func.nodeid: 54}
        assert config.SortConfig.item_bucket_id == {func.nodeid: module.nodeid}
        assert config.SortConfig.bucket_sort_keys == {module.nodeid: 7}

    def test_mode_fastest(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, None, None)
        config.SortConfig.mode = "fastest"
        config.SortConfig.bucket = "class"
        config.SortConfig.bucket_mode = "fastest"
        (session, package, module, cls, func) = mock_objects

        config.SortConfig.item_totals = {
            func.nodeid: 1.1,
            func.nodeid + "_2": 1.1,
        }

        core.create_sort_keys(func, 6, 60)

        assert config.SortConfig.item_sort_keys == {func.nodeid: 1.1}
        assert config.SortConfig.item_bucket_id == {func.nodeid: cls.nodeid}
        assert config.SortConfig.bucket_sort_keys == {cls.nodeid: 2.2}

    def test_min_bucket_key_num(self, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, None, None)
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket = "module"
        config.SortConfig.bucket_mode = "ordered"
        (session, package, module, cls, func) = mock_objects

        core.create_sort_keys(func, 0, 60)
        core.create_sort_keys(func, 1, 60)
        core.create_sort_keys(func, 2, 60)

        assert config.SortConfig.bucket_sort_keys == {module.nodeid: 1}

    @mock.patch("pytest_sort.core.md5")
    def test_min_bucket_key_md5(self, md5, get_marker_settings, mock_objects):
        get_marker_settings.return_value = (None, None, None, None)
        config.SortConfig.mode = "ordered"
        config.SortConfig.bucket = "module"
        config.SortConfig.bucket_mode = "md5"
        (session, package, module, cls, func) = mock_objects

        md5.return_value.digest.side_effect = [b"DEF", b"ABC", b"GHI"]

        core.create_sort_keys(func, 0, 60)
        core.create_sort_keys(func, 1, 60)
        core.create_sort_keys(func, 2, 60)

        assert config.SortConfig.bucket_sort_keys == {module.nodeid: b"ABC"}

    def test_get_item_sort_key(self, mock_objects):
        (session, package, module, cls, func) = mock_objects

        core.SortConfig.item_sort_keys = {func.nodeid: 1.1}
        core.SortConfig.item_bucket_id = {func.nodeid: cls.nodeid}
        core.SortConfig.bucket_sort_keys = {cls.nodeid: 2.2}

        assert core.get_item_sort_key(func) == (2.2, 1.1)


class TestSortItems:
    nodeids = ["function_3", "function_4", "function_1", "function_2"]
    items = [mock.MagicMock(nodeid=nodeid) for nodeid in nodeids]
    node_priority = {"function_1": 1, "function_2": 2, "function_3": 3, "function_4": 4}

    @pytest.fixture
    def random(self):
        with mock.patch("pytest_sort.core.random") as random:
            yield random

    @pytest.fixture
    def get_all_totals(self):
        with mock.patch("pytest_sort.core.get_all_totals") as get_all_totals:
            get_all_totals.return_value = self.node_priority
            yield get_all_totals

    @pytest.fixture
    def create_sort_keys(self):
        with mock.patch("pytest_sort.core.create_sort_keys") as create_sort_keys:
            yield create_sort_keys

    @pytest.fixture
    def get_item_sort_key(self):
        with mock.patch("pytest_sort.core.get_item_sort_key") as get_item_sort_key:
            get_item_sort_key.side_effect = lambda item: self.node_priority[item.nodeid]
            yield get_item_sort_key

    @pytest.fixture
    def print_test_case_order(self):
        with mock.patch("pytest_sort.core.print_test_case_order") as print_test_case_order:
            yield print_test_case_order

    def test_sort_items(self, random, get_all_totals, create_sort_keys, get_item_sort_key, print_test_case_order):
        core.SortConfig.mode = "ordered"
        core.SortConfig.bucket_mode = "ordered"
        core.SortConfig.debug = False

        items = self.items.copy()
        core.sort_items(items)
        assert items[0].nodeid == "function_1"
        assert items[1].nodeid == "function_2"
        assert items[2].nodeid == "function_3"
        assert items[3].nodeid == "function_4"

        random.seed.assert_not_called()
        get_all_totals.assert_not_called()
        create_sort_keys.assert_has_calls(
            [
                mock.call(self.items[0], 0, 4),
                mock.call(self.items[1], 1, 4),
                mock.call(self.items[2], 2, 4),
                mock.call(self.items[3], 3, 4),
            ]
        )
        get_item_sort_key.call_count == 4
        print_test_case_order.assert_not_called()

    @pytest.mark.parametrize(
        "mode,bucket_mode",
        [
            ("random", "ordered"),
            ("ordered", "random"),
            ("random", "random"),
        ],
    )
    def test_sort_items_random(
        self, mode, bucket_mode, random, get_all_totals, create_sort_keys, get_item_sort_key, print_test_case_order
    ):
        core.SortConfig.mode = mode
        core.SortConfig.bucket_mode = bucket_mode
        core.SortConfig.seed = 12345
        core.SortConfig.debug = False

        core.sort_items(self.items.copy())

        random.seed.assert_called_with(12345)
        get_all_totals.assert_not_called()
        assert create_sort_keys.call_count == 4
        assert get_item_sort_key.call_count == 4
        print_test_case_order.assert_not_called()

    @pytest.mark.parametrize(
        "mode,bucket_mode",
        [
            ("fastest", "ordered"),
            ("ordered", "fastest"),
            ("fastest", "fastest"),
        ],
    )
    def test_sort_items_fastest(
        self, mode, bucket_mode, random, get_all_totals, create_sort_keys, get_item_sort_key, print_test_case_order
    ):
        core.SortConfig.mode = mode
        core.SortConfig.bucket_mode = bucket_mode
        core.SortConfig.seed = 12345
        core.SortConfig.debug = False

        core.sort_items(self.items.copy())

        random.seed.assert_not_called()
        get_all_totals.assert_called_with()
        assert create_sort_keys.call_count == 4
        assert get_item_sort_key.call_count == 4
        print_test_case_order.assert_not_called()

    def test_sort_items_debug(self, random, get_all_totals, create_sort_keys, get_item_sort_key, print_test_case_order):
        core.SortConfig.mode = "ordered"
        core.SortConfig.bucket_mode = "ordered"
        core.SortConfig.debug = True

        items = self.items.copy()
        core.sort_items(items)

        random.seed.assert_not_called()
        get_all_totals.assert_not_called()
        assert create_sort_keys.call_count == 4
        assert get_item_sort_key.call_count == 4
        print_test_case_order.assert_called_with(items)


class TestPrintReports:
    @pytest.fixture
    def print(self):
        with mock.patch("builtins.print") as print:
            yield print

    @pytest.fixture
    def get_stats(self):
        with mock.patch("pytest_sort.core.get_stats") as get_stats:
            yield get_stats

    def test_print_recorded_times_report(self, print, get_stats):
        terminal_reporter = mock.MagicMock(
            stats={
                "": [
                    mock.MagicMock(nodeid="function_3"),
                    mock.MagicMock(nodeid="function_4"),
                    mock.MagicMock(nodeid="function_1"),
                    mock.MagicMock(nodeid="function_2"),
                ]
            }
        )

        stats = {
            "function_1": {"setup": 100, "call": 200, "teardown": 300, "total": 600},
            "function_2": {"setup": 100_000, "call": 200_000, "teardown": 300_000, "total": 600_000},
            "function_3": {"setup": 1_000_000, "call": 2_000_000, "teardown": 3_000_000, "total": 6_000_000},
            "function_4": {"setup": 1, "call": 2, "teardown": 3, "total": 6},
        }

        get_stats.side_effect = lambda nodeid: stats[nodeid]

        core.print_recorded_times_report(terminal_reporter)

        print.assert_has_calls(
            [
                mock.call(
                    "\n*** pytest-sort maximum recorded times                        "
                    "Nanoseconds                          ***"
                ),
                mock.call("Test Case                setup             call         teardown            total"),
                mock.call("function_1                 100              200              300              600"),
                mock.call("function_2             100,000          200,000          300,000          600,000"),
                mock.call("function_3           1,000,000        2,000,000        3,000,000        6,000,000"),
                mock.call("function_4                   1                2                3                6"),
            ]
        )

    def test_print_test_case_order(self, print):
        items = [
            mock.MagicMock(nodeid="function_1"),
            mock.MagicMock(nodeid="function_2"),
            mock.MagicMock(nodeid="function_3"),
            mock.MagicMock(nodeid="function_4"),
        ]
        core.SortConfig.item_bucket_id = {
            "function_1": "bucket_1",
            "function_2": "bucket_1",
            "function_3": "bucket_2",
            "function_4": "bucket_2",
        }
        core.SortConfig.bucket_sort_keys = {
            "bucket_1": 1,
            "bucket_2": 2,
        }
        core.SortConfig.item_sort_keys = {
            "function_1": 1,
            "function_2": 2,
            "function_3": 3,
            "function_4": 4,
        }

        core.print_test_case_order(items)

        print.assert_has_calls(
            [
                mock.call("\nTest Case Order:"),
                mock.call("(bucket_key, bucket_id, item_key, item_id)"),
                mock.call((1, "bucket_1", 1, "function_1")),
                mock.call((1, "bucket_1", 2, "function_2")),
                mock.call((2, "bucket_2", 3, "function_3")),
                mock.call((2, "bucket_2", 4, "function_4")),
            ]
        )
