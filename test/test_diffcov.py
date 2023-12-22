import importlib
from pathlib import Path
from unittest import mock

import pytest
from whatthepatch import patch as wtp

from pytest_sort import diffcov


class TestParseTestContext:
    @pytest.mark.parametrize(
        ("context", "nodeid", "when"),
        [
            (
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]|setup",
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]",
                "setup",
            ),
            (
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]|run",
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]",
                "run",
            ),
            (
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]|teardown",
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[1]",
                "teardown",
            ),
            (
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[ABC|DEF]|teardown",
                "test_diffcov.py::TestParseTestContext::test_parse_text_context[ABC|DEF]",
                "teardown",
            ),
        ],
    )
    def test_parse_text_context(self, context, nodeid, when):
        importlib.reload(diffcov)
        match = diffcov.PARSE_TEST_CONTEXT.search(context)

        assert match.group("nodeid", "when") == (nodeid, when)


GIT_DIFF = """diff --git a/pytest_sort/module1.py b/pytest_sort/module1.py
index 404ce22..5f2ed85 100644
--- a/pytest_sort/module1.py
+++ b/pytest_sort/module1.py
@@ -20 +20 @@
- Example Line 1
+ Changed Line 1
@@ -24,1 +24,0 @@
- Example Deleted Line
@@ -30,0 +30,1 @@
+ Example Inserted Line
"""


class TestGitPatch:
    @pytest.fixture()
    def subprocess(self):
        with mock.patch("pytest_sort.diffcov.subprocess") as subprocess:
            yield subprocess

    @pytest.fixture()
    def whatthepatch(self):
        with mock.patch("pytest_sort.diffcov.whatthepatch") as whatthepatch:
            yield whatthepatch

    def test_get_git_toplevel_folder(self, subprocess):
        out = diffcov.get_git_toplevel_folder()

        subprocess.run.assert_called_with(["git", "rev-parse", "--show-toplevel"], capture_output=True, check=True)
        output = subprocess.run.return_value

        assert output.stdout.decode.return_value.strip.return_value == out

    def test_get_git_diff_patch(self, subprocess):
        out = diffcov.get_git_diff_patch()

        subprocess.run.assert_called_with(["git", "diff", "-U0"], capture_output=True, check=True)
        output = subprocess.run.return_value

        assert output.stdout.decode.return_value == out

    def test_get_diff_changed_lines(self):
        assert diffcov.get_diff_changed_lines("C:/dev", GIT_DIFF) == {
            Path("C:/dev/pytest_sort/module1.py").resolve(): {20, 24, 30}
        }

    def test_get_diff_changed_lines_mock(self, whatthepatch):
        whatthepatch.parse_patch.return_value = [
            wtp.diffobj(
                header=wtp.header(
                    old_path="pytest_sort/module1.py",
                    index_path=None,
                    old_version=None,
                    new_path="",
                    new_version=None,
                ),
                changes=[
                    wtp.Change(old=2, new=2, line=None, hunk=0),
                    wtp.Change(old=3, new=None, line=None, hunk=0),
                    wtp.Change(old=None, new=4, line=None, hunk=0),
                    wtp.Change(old=None, new=None, line=None, hunk=0),
                ],
                text="",
            ),
            wtp.diffobj(
                header=wtp.header(
                    old_path="pytest_sort/module2.py",
                    index_path=None,
                    old_version=None,
                    new_path="",
                    new_version=None,
                ),
                changes=[
                    wtp.Change(old=20, new=2, line=None, hunk=0),
                ],
                text="",
            ),
        ]

        assert diffcov.get_diff_changed_lines("C:/dev", GIT_DIFF) == {
            Path("C:/dev/pytest_sort/module1.py").resolve(): {0, 2, 3, 4},
            Path("C:/dev/pytest_sort/module2.py").resolve(): {20},
        }

        whatthepatch.parse_patch.assert_called_with(GIT_DIFF)

    def test_get_diff_changed_lines_no_header(self, whatthepatch):
        whatthepatch.parse_patch.return_value = [
            wtp.diffobj(
                header=None,
                changes=[
                    wtp.Change(old=2, new=2, line=None, hunk=0),
                    wtp.Change(old=3, new=None, line=None, hunk=0),
                    wtp.Change(old=None, new=4, line=None, hunk=0),
                    wtp.Change(old=None, new=None, line=None, hunk=0),
                ],
                text="",
            ),
        ]

        assert diffcov.get_diff_changed_lines("C:/dev", GIT_DIFF) == {}

    def test_get_diff_changed_lines_no_changes(self, whatthepatch):
        whatthepatch.parse_patch.return_value = [
            wtp.diffobj(
                header=wtp.header(
                    old_path="pytest_sort/module1.py",
                    index_path=None,
                    old_version=None,
                    new_path="",
                    new_version=None,
                ),
                changes=None,
                text="",
            )
        ]

        assert diffcov.get_diff_changed_lines("C:/dev", GIT_DIFF) == {}


class TestMutChangedLines:
    def test_get_mut_changed_lines(self):
        os_environ = {
            "MUT_SOURCE_FILE": "pytest_sort/module1.py",
            "MUT_LINENO": "20",
            "MUT_END_LINENO": "30",
        }
        with mock.patch.dict("pytest_sort.diffcov.os.environ", os_environ, clear=True):
            assert diffcov.get_mut_changed_lines() == {
                Path("pytest_sort/module1.py").resolve(): {20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30},
            }

    def test_get_mut_changed_lines_default_end(self):
        os_environ = {
            "MUT_SOURCE_FILE": "pytest_sort/module1.py",
            "MUT_LINENO": "20",
        }
        with mock.patch.dict("pytest_sort.diffcov.os.environ", os_environ, clear=True):
            assert diffcov.get_mut_changed_lines() == {
                Path("pytest_sort/module1.py").resolve(): {20},
            }

    def test_get_mut_changed_lines_no_lineno(self):
        os_environ = {
            "MUT_SOURCE_FILE": "pytest_sort/module1.py",
        }
        with mock.patch.dict("pytest_sort.diffcov.os.environ", os_environ, clear=True):
            assert diffcov.get_mut_changed_lines() == {}

    def test_get_mut_changed_lines_no_source(self):
        os_environ = {
            "MUT_LINENO": "20",
        }
        with mock.patch.dict("pytest_sort.diffcov.os.environ", os_environ, clear=True):
            assert diffcov.get_mut_changed_lines() == {}


class TestCoverage:
    @pytest.fixture()
    def CoverageData(self):
        with mock.patch("pytest_sort.diffcov.CoverageData") as CoverageData:  # noqa: N806
            yield CoverageData

    def test_get_line_coverage(self, CoverageData):
        cov = CoverageData.return_value
        cov.measured_files.return_value = ["pytest_sort/module1.py", "pytest_sort/module2.py"]
        cov.contexts_by_lineno.side_effect = [
            {
                1: [
                    "test_diffcov.py::test_get_line_coverage_1|setup",
                    "test_diffcov.py::test_get_line_coverage_2|setup",
                ],
                11: ["test_diffcov.py::test_get_line_coverage_1|run"],
                22: ["test_diffcov.py::test_get_line_coverage_2|run"],
                100: ["test_diffcov.py::test_get_line_coverage_1|teardown"],
            },
            {
                1: ["test_diffcov.py::test_get_line_coverage_1|run"],
                2: ["test_diffcov.py::test_get_line_coverage_1"],
            },
        ]

        line_coverage = diffcov.get_line_coverage()

        assert next(line_coverage) == (
            Path("pytest_sort/module1.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_1",
            "setup",
            1,
        )
        assert next(line_coverage) == (
            Path("pytest_sort/module1.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_2",
            "setup",
            1,
        )
        assert next(line_coverage) == (
            Path("pytest_sort/module1.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_1",
            "run",
            11,
        )
        assert next(line_coverage) == (
            Path("pytest_sort/module1.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_2",
            "run",
            22,
        )
        assert next(line_coverage) == (
            Path("pytest_sort/module1.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_1",
            "teardown",
            100,
        )
        assert next(line_coverage) == (
            Path("pytest_sort/module2.py").resolve(),
            "test_diffcov.py::test_get_line_coverage_1",
            "run",
            1,
        )
        with pytest.raises(StopIteration):
            next(line_coverage)


class TestGetScores:
    @pytest.fixture()
    def get_git_toplevel_folder(self):
        with mock.patch("pytest_sort.diffcov.get_git_toplevel_folder") as get_git_toplevel_folder:
            yield get_git_toplevel_folder

    @pytest.fixture()
    def get_git_diff_patch(self):
        with mock.patch("pytest_sort.diffcov.get_git_diff_patch") as get_git_diff_patch:
            yield get_git_diff_patch

    @pytest.fixture()
    def get_diff_changed_lines(self):
        with mock.patch("pytest_sort.diffcov.get_diff_changed_lines") as get_diff_changed_lines:
            yield get_diff_changed_lines

    @pytest.fixture()
    def get_mut_changed_lines(self):
        with mock.patch("pytest_sort.diffcov.get_mut_changed_lines") as get_mut_changed_lines:
            yield get_mut_changed_lines

    @pytest.fixture()
    def get_line_coverage(self):
        with mock.patch("pytest_sort.diffcov.get_line_coverage") as get_line_coverage:
            yield get_line_coverage

    @pytest.fixture()
    def get_test_scores(self):
        with mock.patch("pytest_sort.diffcov.get_test_scores") as get_test_scores:
            yield get_test_scores

    def test_get_test_scores(self, get_line_coverage):
        rpath_m1 = Path("pytest_sort/module1.py").resolve()
        rpath_m2 = Path("pytest_sort/module2.py").resolve()
        rpath_m3 = Path("pytest_sort/module3.py").resolve()

        changed_lines = {
            rpath_m1: {1, 2, 3, 4, 5, 6, 7, 8, 9},
            rpath_m2: {1, 2, 3, 4, 5, 6, 7, 8, 9},
        }

        get_line_coverage.return_value = [
            (rpath_m1, "test_diffcov.py::covers_changes", "setup", 1),
            (rpath_m1, "test_diffcov.py::covers_changes", "setup", 2),
            (rpath_m1, "test_diffcov.py::covers_changes", "run", 3),
            (rpath_m1, "test_diffcov.py::covers_changes", "run", 4),
            (rpath_m1, "test_diffcov.py::covers_changes", "teardown", 5),
            (rpath_m1, "test_diffcov.py::covers_changes", "teardown", 6),
            # Covers other module only
            (rpath_m3, "test_diffcov.py::no_cov", "run", 1),
            # Covers module, but no Coverage on changed lines
            (rpath_m2, "test_diffcov.py::cov_mod_not_line", "setup", 100),
            (rpath_m2, "test_diffcov.py::cov_mod_not_line", "run", 100),
            (rpath_m2, "test_diffcov.py::cov_mod_not_line", "teardown", 100),
            # Only covers change in setup
            (rpath_m2, "test_diffcov.py::cov_setup", "setup", 1),
            # Only covers change in run
            (rpath_m2, "test_diffcov.py::cov_run", "run", 1),
            # Only covers change in teardown
            (rpath_m2, "test_diffcov.py::cov_teardown", "teardown", 1),
        ]

        assert diffcov.get_test_scores(changed_lines) == {
            "test_diffcov.py::covers_changes": -15,
            "test_diffcov.py::cov_mod_not_line": -1,
            "test_diffcov.py::cov_setup": -2,
            "test_diffcov.py::cov_run": -6,
            "test_diffcov.py::cov_teardown": -2,
        }

    def test_get_diff_test_scores(
        self,
        get_test_scores,
        get_git_toplevel_folder,
        get_git_diff_patch,
        get_diff_changed_lines,
    ):
        assert diffcov.get_diff_test_scores() == get_test_scores.return_value
        get_git_toplevel_folder.assert_called_once()
        get_git_diff_patch.assert_called_once()
        get_diff_changed_lines.assert_called_once_with(
            get_git_toplevel_folder.return_value,
            get_git_diff_patch.return_value,
        )

    def test_get_mut_test_scores(
        self,
        get_test_scores,
        get_mut_changed_lines,
    ):
        assert diffcov.get_mut_test_scores() == get_test_scores.return_value
        get_mut_changed_lines.assert_called_once()
