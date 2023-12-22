"""Logic for prioritizing tests by coverage of changes."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Generator

import whatthepatch
from coverage.sqldata import CoverageData

# pytest-cov populates test context as <nodeid>|(setup|run|teardown)
PARSE_TEST_CONTEXT = re.compile(r"(?P<nodeid>.*)\|(?P<when>setup|run|teardown)")


def get_git_toplevel_folder() -> str:
    """Run Git rev-parse to get toplevel folder name."""
    output = subprocess.run(shlex.split("git rev-parse --show-toplevel"), capture_output=True, check=True)  # noqa: S603
    return output.stdout.decode().strip()


def get_git_diff_patch() -> str:
    """Run Git Diff command and return result as string."""
    output = subprocess.run(shlex.split("git diff -U0"), capture_output=True, check=True)  # noqa: S603
    return output.stdout.decode()


def get_diff_changed_lines(git_folder: str, git_diff_patch: str) -> dict[Path, set[int]]:
    """Use whatthepatch to parse the patch string.

    Return map of resolved path of file to set of inserted, updated, or deleted line numbers.
    """
    changed_lines = {}
    patch_data = whatthepatch.parse_patch(git_diff_patch)
    for diff in patch_data:
        if diff.header and diff.changes:
            path = diff.header.old_path
            rpath = Path(git_folder).joinpath(path).resolve()
            changed_lines[rpath] = {change.old or change.new or 0 for change in diff.changes}
    return changed_lines


def get_mut_changed_lines() -> dict[Path, set[int]]:
    """Use environment variables set by mutation testing tool to determine changed lines.

    Return map of resolved path of file to set of inserted, updated, or deleted line numbers.
    """
    changed_lines = {}
    mut_source_file = os.environ.get("MUT_SOURCE_FILE", None)
    mut_lineno = os.environ.get("MUT_LINENO", 0)
    mut_end_lineno = os.environ.get("MUT_END_LINENO", mut_lineno)

    if mut_source_file and mut_lineno:
        rpath = Path(mut_source_file).resolve()
        changed_lines[rpath] = set(range(int(mut_lineno), int(mut_end_lineno) + 1))

    return changed_lines


def get_line_coverage() -> Generator[tuple[Path, str, str, int], Any, None]:
    """Retrieve coverage data from coverage.py.

    Return flattened data as (resolved_path, nodeid, when, line).
    """
    cov = CoverageData()
    cov.read()
    for path in cov.measured_files():
        rpath = Path(path).resolve()
        for line, tests in cov.contexts_by_lineno(path).items():
            for test in tests:
                match = PARSE_TEST_CONTEXT.search(test)
                if match:
                    (nodeid, when) = match.group("nodeid", "when")
                    yield rpath, nodeid, when, line


def get_test_scores(changed_lines: dict[Path, set[int]]) -> dict[str, int]:
    """Genarate a 'score' for each test case that has some coverage of the changed lines."""
    test_scores = {}
    for rpath, nodeid, when, line in get_line_coverage():
        if rpath in changed_lines:
            # If test coverage includes changed module
            if nodeid not in test_scores:
                test_scores[nodeid] = -1
            # If test coverage includes changed line
            if line in changed_lines[rpath]:
                # Changed line covered in run phase
                if when == "run":
                    test_scores[nodeid] -= 5
                # Changed line covered in setup or terminate phase
                else:
                    test_scores[nodeid] -= 1
    return test_scores


def get_diff_test_scores() -> dict[str, int]:
    """Genarate a 'score' for each test case that has some coverage of the changed files."""
    return get_test_scores(get_diff_changed_lines(get_git_toplevel_folder(), get_git_diff_patch()))


def get_mut_test_scores() -> dict[str, int]:
    """Genarate a 'score' for each test case that has some coverage of the mutated lines."""
    return get_test_scores(get_mut_changed_lines())
