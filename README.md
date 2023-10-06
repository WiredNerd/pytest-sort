![python>=3.8](https://img.shields.io/badge/python->=3.8-blue)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytest-sort)
![PyPI - License](https://img.shields.io/pypi/l/pytest-sort)
![PyPI - Version](https://img.shields.io/pypi/v/pytest-sort)

[![Code Coverage](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fcode-coverage.json&query=%24.totals.percent_covered_display&suffix=%25&label=Code%20Coverage&color=teal)](https://pytest-cov.readthedocs.io)
[![Mutation Coverage](https://img.shields.io/badge/dynamic/xml?url=https%3A%2F%2Fraw.githubusercontent.com%2FWiredNerd%2Fpytest-sort%2Fmain%2Fmutation-testing-report.xml&query=round((%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled%20-%20%2F%2Ftestsuites%5B1%5D%2F%40failures%20-%20%2F%2Ftestsuites%5B1%5D%2F%40errors)div(%2F%2Ftestsuites%5B1%5D%2F%40tests%20-%20%2F%2Ftestsuites%5B1%5D%2F%40disabled)*100)&suffix=%25&label=Mutation%20Coverage&color=orange)](https://mutmut.readthedocs.io/)

[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Code Style: black](https://img.shields.io/badge/Code_Style-Black-black)](https://black.readthedocs.io)
[![Linter: ruff](https://img.shields.io/badge/Linter-ruff-purple)](https://beta.ruff.rs/docs/)
[![Snyk Security](https://img.shields.io/badge/Snyk%20Security-monitored-FF66FF)](https://snyk.io/)
[![Documentation Status](https://readthedocs.org/projects/pytest-sort/badge/?version=docs)](https://pytest-sort.readthedocs.io/)


## Project description

pytest-sort is a pytest plugin to automatically change the execution order of test cases.  Changing the order of execution can help find test cases that only succeed because of a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

## Quick Start

Installation:

```
pip install pytest-sort --upgrade
```

Running with pytest-sort:

```
pytest --sort-mode=random
```

By default, all tests from the same module or class will run together.  This command will randomize the execution order of the tests within the module/class.

```
pytest --help
```

In the pytest-sort section, all currently avaialable options will be listed.

You may also set options in any [pytest configruation file](https://docs.pytest.org/en/stable/reference/customize.html).
