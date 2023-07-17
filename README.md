![python>=3.8](https://img.shields.io/badge/python->=3.8-blue)

## Project description

pytest-sort is a pytest plugin to automatically change the execution order of test cases.  Changing the order of execution can help find test cases that only succeed because a different test left the system in a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

## Quick Start

Installation:

```
pip install pytest-sort -upgrade
```

Running with pytest-sort:

```
pytest --sort_mode=random
```

By default, all tests from the same module will run together.  This command will run the tests within the module in a random order.

```
pytest --help
```

In the pytest-sort section, all currently avaialable options will be listed.

You may also set options in any [pytest configruation file](https://docs.pytest.org/en/stable/reference/customize.html).

## Options

### Sort Bucket

***Default:*** module

This option controls the scope of the sort operation.  For example, if the sort bucket is "module", then all tests from the same module will run together.  If the sort bucket is global, than all tests are sorted together.

Example: 
```
pytest --sort_bucket=package
```

| sort_bucket | Definition | 
| --- | --- |
| global | Apply sort to all items together |
| package | Group together test cases that are in the same package (folder) |
| module | Group together test cases that are in the same module (py file) |
| class | Group together test cases that are members of a class.  All other test cases are grouped by module |
| parent | Group together test cases by their immediate parent |
| grandparent | Group together test cases by their parent's parent |

### Sort Mode

***Default:*** none

This option controlls how the order is modified within the bucket.

Example:
```
pytest --sort_mode=md5
```

| sort_mode | Definition | 
| --- | --- |
| none | pytest_sort will not modify the sort order.  This option disables pytest_sort. |
| md5 | This mode creates an md5 of each test case id, then sorts on those values.  <br> This runs test cases in a deterministicly shuffled order. |
| random | Test cases are shuffled randomly |
| fastest | In each run in "fasttest" mode, the plugin will track the longest execution time for each test case in a file '.pytest-sort'.  <br> At the beginning of a test run, any previously recorded values will be used to sort the tests so that the fastest test runs first.<br>  This is intended for use with "-x" or "--exitfirst"