# Pytest Sort

[![PyPI - Version](https://img.shields.io/pypi/v/pytest-sort)](https://pypi.org/project/pytest-sort)
[![Homepage](https://img.shields.io/badge/Homepage-github-white)](https://github.com/WiredNerd/pytest-sort)

This Pytest plugin is used to help identify [Application State Leaks](project:app_state_leaks.md) in your test suite.
It does this by automatically changing the execution order of test cases.

How frustrating is it to have a test case that works fine when runs by itself, but fails when run with the rest of the suite?
By running tests in a random order, the culprit of such problems can be identified much earlier in the development process.
Alternately, running in ordered and reverse order can help find the cause of the problem in existing test suites.

## Features

* Multiple sort options including: Randomly, Fastest, Ordered, Reverse, and more.
* Group test cases into buckets that are each sorted separately.
* Control sort order of the buckets.
* Use Pytest markers to always run specific test cases in order.

## Installation

```
pip install pytest-sort --upgrade
```

## Running

```
pytest --sort-mode=random
```

```{toctree}
:maxdepth: 2
:caption: Contents
app_state_leaks.md
usage.md
configuration.md
mutation_testing.md
```

