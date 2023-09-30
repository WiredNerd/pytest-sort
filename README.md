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


## Project description

pytest-sort is a pytest plugin to automatically change the execution order of test cases.  Changing the order of execution can help find test cases that only succeed because of a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

## Quick Start

Installation:

```
pip install pytest-sort -upgrade
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

# Usage

Ideally, all test cases should be small and independant. And should cleanup any changes to the application state.  This package provides several options for validating if test cases can really be run independantly and cleanly.

## Deterministic but Unpredictable

Java developers will be farmilliar with JUnit. The JUnit package automatically runs test cases in a deterministic, but unpredictable order.  This package can provide similar functionality in pytest several ways.

1. Using sort mode "md5" will produce the same order of tests every time as long as the test case names don't change.
   ```toml
   sort_mode="md5"
   ```
2. Using sort mode "random" with a fixed sort seed value will produce the same order of tests every time unles the list of test cases is changed (new test case, or name changes)
   ```toml
   sort_mode="random"
   sort_seed=100
   ```

## Random

By running in random mode, the test case order will change every time. If a test case fails unexpectedly, you can use the seed from the failed run to determine what order is causing the tests to fail.

```toml
sort_mode="random"
```

## Fail Fast

When you have a test suite that includes long running test cases, it can be helpful to delay the longer running test cases till later.  The 'fastest' mode allows you to track how long different test cases take to run.  Then always run the fastest test cases first, and the slow test cases last.
```cmd
pytest --exitfirst --sort-mode=fastest
```

## Mutation Testing

Mutuation testing is slow.  The 'diffcov' mode can help accelerate mutation testing.

The mutuation testing tool 'mutmut' works by modifying the source code, then running pytest to see if any tests catch the change.  Using 'git diff' and 'coverage.py' the 'diffcov' mode combines the differences detected by Git with the coverage information recorded by coverage.py to prioritize test cases.  That way the test cases most likely to catch the change are run as early as possible.

Steps to use 'diffcov' mode:
1. Run pytest with coverage and context.  This records the coverage for each test case as a separate context.
```
pytest --cov= --cov-context=test
```
2. Run mutmut with runner options.
```
mutmut run --runner "pytest --exitfirst --assert=plain --sort-mode=diffcov"
```

You can also combine with 'fastest' to run tests with same coverage from fastest to slowest:
```
pytest --cov= --cov-context=test --sort-mode=fastest
mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=diffcov --sort-bucket=function --sort-mode=fastest"
```

# How it Works

Pytest gathers a list of test cases to be executed, by default it orders test cases from top to bottom of each file.  This plugin takes that list and creates two sort keys.  The first is a sort key for each bucket, and the second is a sort key for each test.  It then sorts the list of test cases using the two sort keys.

Bucket is simply a group of test cases.  Depending on the sitation it can be better to keep test cases grouped together.  For example, if the test suite includes fixtures with a scope of module, it would be best to use a bucket type of module, class, or parent.  This is becasue pytest will create that fixture every time testing eneters the module, and destroy it every time thesting leaves the module.

You can also separately control the sorting method for buckets and for test cases.  For example, if you wanted to always run the modules in order provided by pytest, but wanted to randomize test order within each module.  This can be achived by setting the Sort Mode to 'random', and the Bucket Sort Mode to 'ordered'.

# Pytest Markers

## sort(mode,bucket)

```py
sort(mode: str, bucket: str = "self")
```

The 'sort' marker allows you to change the sort settings for the marked module or class. 
* 'mode' argument is required, and changes the [Sort Mode](#sort-mode) setting for all tests within the marked module or class.
* 'bucket' argument is optional.  By default, the sort marker will set the bucket for all tests in the marked scope to be the marked module or class.  But any other valid [Sort Bucket](#sort-bucket) can be set instead.

Usage Examples:
```py
import pytest

pytestmark = pytest.mark.sort("random", bucket="package")

def test_that_cba_works():  # This test case is grouped with other tests in the package bucket, and sorted randomly.
   ...

@pytest.mark.sort("ordered")
class TestClassAbc:
   def test_that_abc_works(self): # This test case is grouped with other tests in class TestClassAbc and kept in order listed.
      ...
```

## order(item_sort_key)

```py
def order(item_sort_key: Any)
```

The 'order' marker sets the sort key for the marked test, class, or module to the provided value.
* The 'sort_key' value is required, and can be any value that can be used as a list sort key

When used to mark a test function, the sort key for that item is set to the priovided value.

When used to mark a test Class or Module, the Class or Module is used as a bucket for all test within it, and the sort key for the bucket is set to the provided value.

Usage Example:
```py
import pytest

pytestmark = pytest.mark.order("my_tests")

@pytest.mark.order("test_group_1")
class TestClass:
   @pytest.mark.order(1)
   def test_create_the_data():  # bucket_key="test_group_1", item_key=1
      ...
   @pytest.mark.order(2)
   def test_modify_the_data():  # bucket_key="test_group_1", item_key=2
      ...
   @pytest.mark.order(3)
   def test_validate_the_data():  # bucket_key="test_group_1", item_key=3
      ...

@pytest.mark.order("ZZZ")
   def test_delete_the_data():  # bucket_key="my_tests", item_key="ZZZ"
      ...
```

# Options

For all options, the priority of options is:
1. Pytest Markers (closest to the test case)
2. Command Line Option
3. Pytest Config Option
4. Default values

## Sort Mode

This option controlls how the order is modified within each bucket.

***Command Line:*** `--sort-mode`

***Pytest Config:*** `sort_mode`

***Default:*** `ordered`

| Option | Definition | 
| --- | --- |
| ordered | (default) pytest_sort will keep the default order of tests. |
| reverse |pytest_sort will reverse the default order of tests. |
| md5 | This mode creates an md5 of each test case id, then sorts on those values.  <br> This runs test cases in a deterministicly shuffled order. |
| random | Test cases are shuffled randomly. Sort Seed is used to control random sorting. |
| fastest | In each run in "fastest" mode, any previously recorded runtimes in ".pytest_sort_data" file will be used to sort the fastest tests to run first.  Also, by default, it will record the longest execution time for each test case to that file for future usage.  See [Record Test Runtimes](#record-test-runtimes) |
| diffcov | Uses 'git diff' and data from 'coverage.py' to determine which test cases likey cover the changed lines of code, and runs them first. |

## Sort Bucket

Sort test order within specified test buckets.

For example, if the sort bucket is "module", then all tests from the same module will be completed before running tests for the next module.

***Command Line:*** `--sort-bucket`

***Pytest Config:*** `sort_bucket`

***Default:*** `parent`

| Option | Definition | 
| --- | --- |
| session | Apply sort to all items together. |
| package | Group together test cases that are in the same package (folder). |
| module | Group together test cases that are in the same module (py file). |
| class | Group together test cases that are members of a class.  <br>All other (non-class) test cases are grouped by module. |
| function | Each test function is assigned a separate bucket. |
| parent | Group together test cases by their immediate parent. |
| grandparent | Group together test cases by their parent's parent. |

> Sort buckets higher than class or parent can cause fixtures to be teardown and setup more than expected.
<br>For example: If sort bucket is "package" and fixture scope is "module", Pytest may setup the fixture every time the testing enters the module, and teardown each time testing leaves the module.
<br>The option --setup-show can reveal when fixtures are created and destroyed.

## Bucket Sort Mode

This option controlls how the order is modified within each bucket.

***Command Line:*** `--sort-bucket-mode`

***Pytest Config:*** `sort_bucket_mode`

***Default:*** `sort_mode`

| Option | Definition | 
| --- | --- |
| sort_mode | (default) Use the same sort mode for buckets as used for tests.  See [Sort Mode](#sort-mode) |
| ordered | pytest_sort will keep the default order of buckets. |
| reverse | pytest_sort will reverse the default order of buckets. |
| md5 | This mode creates an md5 of each bucket's id, then sorts on those values. |
| random | Buckets are shuffled randomly. Sort Seed is used to control random sorting. |
| fastest | The total of all runtimes for tests in the bucket is used as the sort key for the bucket. |
| diffcov | Uses 'git diff' and data from 'coverage.py' to determine which test cases likey cover the changed lines of code, and runs them first. |

## Sort Seed

Only used in "random" sort mode.  This field allows you to manually set the seed used by random package when sorting tests.

> Tip: Seed is printed in the pytest header

***Command Line:*** `--sort-seed`

***Pytest Config:*** `sort_seed`

***Default:*** A random integer between 0 and 1,000,000 generated at runtime.

## Record Test Runtimes

When this option is enabled, this plugin with collect runtime information for all tests. If the recorded values are higher than values already stored in ".pytest_sort_data" file, the values in the file are updated.

When Sort Mode or Bucket Sort Mode is 'fastest' this option is enabled by default.

For any othe Sort Mode, this option is disabled by default.

***Command Line:*** `--sort-record-times/--sort-no-record-times`

***Pytest Config:*** `sort_record_times`

***Default:*** false 

| Option | Definition |
| --- | --- |
| `--sort-record-times`<br>`sort_record_times=true` | Enable recording the maximum test case runtimes. |
| `--sort-no-record-times`<br>`sort_record_times=false` | Disable recording test case runtimes. |

## Reset Recorded Test Runtimes

Clear all recorded runtimes before sorting and running the next test.

When recording runtimes, only the highest runtime values for each test case are retained.  After significant changes to test cases that can change how fast they run, it is advisable to reset the runtimes.  This can help maintain more accurate sorting in "fastest" mode.

> Runtimes can also be deleted by deleting the '.pytest_sort_data' file.

***Command Line:*** `--sort-reset-times`

***Pytest Config:*** N/A

## Report Recorded Test Runtimes

At the end of the test run, print out the currently saved test runtimes.

***Command Line:*** `--sort-reset-times`

***Pytest Config:*** N/A

## Recorded Test Runtimes Datafile

Change the location and/or name of the datafile used to store the test runtimes.

***Command Line:*** `--sort-datafile`

***Pytest Config:*** `sort_datafile`

***Default:*** `.pytest_sort_data` 

