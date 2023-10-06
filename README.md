![python>=3.8](https://img.shields.io/badge/python->=3.8-orange)
[![PyPI - Version](https://img.shields.io/pypi/v/pytest-sort)](https://github.com/WiredNerd/pytest-sort)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-sort)

[![Code Coverage](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fcode-coverage.json&query=%24.totals.percent_covered_display&suffix=%25&label=Code%20Coverage&color=teal)](https://pytest-cov.readthedocs.io)
[![Mutation Coverage](https://img.shields.io/badge/dynamic/xml?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fmutation-testing-report.xml&query=round((%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled%20-%20%2F%2Ftestsuites%5B1%5D%2F%40failures%20-%20%2F%2Ftestsuites%5B1%5D%2F%40errors)div(%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled)*100)&suffix=%25&label=Mutation%20Coverage&color=orange)](https://mutmut.readthedocs.io/)
[![Documentation Status](https://readthedocs.org/projects/pytest-sort/badge/?version=docs)](https://pytest-sort.readthedocs.io/)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code Style: black](https://img.shields.io/badge/Code_Style-Black-black)](https://black.readthedocs.io)
[![Linter: ruff](https://img.shields.io/badge/Linter-ruff-purple)](https://beta.ruff.rs/docs/)
[![Snyk Security](https://img.shields.io/badge/Snyk%20Security-monitored-FF66FF)](https://snyk.io/)
[![PyPI - License](https://img.shields.io/pypi/l/pytest-sort)](https://github.com/WiredNerd/pytest-sort/blob/main/LICENSE)


# Pytest-Sort

This pytest plugin is used to help identify application state leaks in your test suite.  It does this by automatically changing the execution order of test cases.

How fustrating is it to have a test case that works fine when runs by itself, but fails when run with the rest of the suite?  By running tests in a random order, the culprit of such problems can be identified much earlier in the development process.  Alternately, running in ordered and reverse order can help find the cause of the problem in existing test suites.

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

## Contribute

- Issue Tracker: https://github.com/WiredNerd/pytest-sort/issues
- Source Code: https://github.com/WiredNerd/pytest-sort

## Support

If you are having issues, please let us know.

I can be contacted at: pbuschmail-pytestsort@yahoo.com

Or by opening an issue: https://github.com/WiredNerd/pytest-sort/issues

## License

The project is licensed under the MIT license.