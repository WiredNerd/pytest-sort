[![Homepage](https://img.shields.io/badge/Homepage-github-white?logo=github)](https://github.com/WiredNerd/pytest-sort)
[![python>=3.8](https://img.shields.io/badge/python->=3.8-orange?logo=python&logoColor=green)](https://pypi.org/project/pytest-sort)
[![PyPI - Version](https://img.shields.io/pypi/v/pytest-sort?logo=pypi&logoColor=white)](https://pypi.org/project/pytest-sort)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-sort)](https://pypistats.org/packages/pytest-sort)
[![PyPI - License](https://img.shields.io/pypi/l/pytest-sort)](https://github.com/WiredNerd/pytest-sort/blob/main/LICENSE)

[![Code Coverage](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fcode-coverage.json&query=%24.totals.percent_covered_display&suffix=%25&label=Code%20Coverage&color=teal&logo=pytest&logoColor=green)](https://pytest-cov.readthedocs.io)
[![Mutation Coverage](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fmutation-testing-report.json&query=%24.summary.coverage_display&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTM1Ljc1bW0iIGhlaWdodD0iMTE4Ljc1bW0iIHZlcnNpb249IjEuMSIgdmlld0JveD0iMCAwIDEzNS43NSAxMTguNzUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI%2BCiA8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtNDAuOTg4IC01Ni43NjUpIiBzdHJva2U9IiMwMDAiPgogIDxwYXRoIGQ9Im02Ny42NDMgMTU3LjE4Yy04LjUwMi00LjU1NjMtMTUuNzM3LTEyLjA5Ny0xNy43NjgtMjEuNzY4LTMuMDE0OC0xMi40MzEtMi44MDAxLTI1LjQ3LTEuMTU0Mi0zOC4wNzcgMS43Mzc5LTExLjA0NCAxMC44NzktMTguNzAzIDE5LjIzNy0yNS4xNCA3Ljk1NjItNS4zNTg3IDE2Ljc3Mi0xMC4wNzUgMjYuMjE3LTExLjk1NyAxMS4zNzctMS4zNjgxIDI0Ljk5NC0xLjMzODYgMzMuMTY0IDguMDQyOSAzLjk4MjQgNC4yMTQ0IDUuNTI1OCAxMC4wMzEgNC45NjY3IDE1LjcwMS0wLjAzODkgNy4xNTQgMi40MjM2IDE1LjIxMyA5LjQwOTMgMTguNDU1IDkuMTIxNSA1LjIyODUgMjAuMTgxIDQuNDEwNiAyOS42NzUgOC42MTg3IDUuNzA5IDUuODg3NS0yLjAzNzEgMTMuMDI4LTQuMDcxNyAxOC44NTktMi43MDMzIDcuNDQxNS0xMC4zMTcgOS44Njg2LTE3LjAxIDEyLjM1Ny0xMy4wMzYgNS4xNy0yNC44NDcgNy43MDExLTQxLjUxMSAxMS4yNDYtMjIuMDk5IDUuNTk4NS0zMC43MzMgNS45NjU2LTQxLjE1NCAzLjY2MjN6IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9IjkiLz4KICA8Zz4KICAgPHBhdGggZD0ibTE2Mi42NyAxMzAuNzJjLTUuNDczNCAwLjU3NjYtMTEuMTc2LTkuODU5MS0xMC43NDgtMTUuNzc3IDEuNjYwMy03Ljk1NCA2Ljc3NDUtMi4wMDg5IDguOTc0NS0zLjE4NDkgMi4wMjAyLTEuMDcxIDQuMDg0MS0xLjMyNjIgNi4yMTE2LTAuMzkzMzIgNC44MzAyIDIuNzA4NyAwLjkxNDE1IDEwLjI2LTEuMDk3NyAxMy45ODV6IiBzdHJva2Utd2lkdGg9IjkiIGZpbGw9IiMwMDAiLz4KICAgPGVsbGlwc2UgY3g9IjExNy4xMSIgY3k9IjEwNi4wNyIgcng9IjEwLjc1IiByeT0iNi40MTEzIiBzdHJva2Utd2lkdGg9IjkiIGZpbGw9IiMwMDAiLz4KICAgPHBhdGggZD0ibTgxLjAyMiA4Ny41M2M1LjU0OTEgMi40MjY3IDQuODU2MiAyLjcxMzMgNC43NDY3IDcuMjgwMS0wLjA5MTkgMTMuNDMgNS4xNzE0IDI2Ljc2IDQuODE1NSA0MC42NzggMC4xMjQ5IDYuMDMxMS0xLjA0MTkgMTAuMjA1LTMuNjk1NiAxNy41MTYtNS45MjY5IDIuNzI3My0xMi41NjkgNS40ODE0LTE5LjI0NSA0LjE3MzgtNi45NjUzLTQuOTI2OC0xMy4yMTUtNy40NDMzLTE2LjQwMS0xNy4zODctMy40MDgzLTE0LjU1OC01Ljc0MjYtMzIuMTI2LTEuMzgwNS00NS4zNTkgMS41MTItNy42OTEyIDI4LjMyMi04LjEzMTkgMzEuMTU5LTYuOTAyNCIgc3Ryb2tlLXdpZHRoPSI5IiBmaWxsPSIjMDAwIi8%2BCiAgPC9nPgogPC9nPgo8L3N2Zz4%3D&label=Mutation%20Coverage&color=3A438C)](https://poodle.readthedocs.io/)
[![Documentation](https://img.shields.io/badge/Read%20the%20Docs-pytest_sort-blue?logo=readthedocs&logoColor=FFF)](https://pytest-sort.readthedocs.io/)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code Style: black](https://img.shields.io/badge/Code_Style-Black-black?logo=python&logoColor=black)](https://black.readthedocs.io)
[![Linter: ruff](https://img.shields.io/badge/Linter-ruff-purple?logo=Ruff)](https://beta.ruff.rs/docs/)
[![Snyk Security](https://img.shields.io/badge/Snyk%20Security-monitored-939?logo=snyk)](https://snyk.io/)



# Pytest-Sort

This pytest plugin is used to help identify application state leaks in your test suite.  It does this by automatically changing the execution order of test cases.

How frustrating is it to have a test case that works fine when runs by itself, but fails when run with the rest of the suite?  By running tests in a random order, the culprit of such problems can be identified much earlier in the development process.  Alternately, running in ordered and reverse order can help find the cause of the problem in existing test suites.

## Features

* Multiple sort options including: Random, Fastest, Reverse, and more.
* Group test cases into buckets that are each sorted separately.
* Control sort order of the buckets.
* Use Pytest markers to always run specific test cases in order.

## Quick Start

Installation:

```
pip install pytest-sort --upgrade
```

Running with pytest-sort:

```
pytest --sort-mode=random
```

## Documentation:

- Usage, Examples, Configuration, and more: https://pytest-sort.readthedocs.io/

## Contribute

- Issue Tracker: https://github.com/WiredNerd/pytest-sort/issues
- Source Code: https://github.com/WiredNerd/pytest-sort

## Support

If you are having issues, please let us know.

I can be contacted at: pbuschmail-pytestsort@yahoo.com

Or by opening an issue: https://github.com/WiredNerd/pytest-sort/issues

## License

The project is licensed under the MIT license.