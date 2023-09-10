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

By default, all tests from the same module or class will run together.  This command will randomize the execution order of the tests within the module/class.

```
pytest --help
```

In the pytest-sort section, all currently avaialable options will be listed.

You may also set options in any [pytest configruation file](https://docs.pytest.org/en/stable/reference/customize.html).

## Options

<<<<<<< Updated upstream
### Sort Bucket
=======
Ideally, all test cases should be small and independant. And they should cleanup anything they change in the state of the applciation.  This package provides several options for validating if test cases can really be run safely, or if they have ordering dependencies. Additionally, if some tests need to be run in order intentionally, pytest markers are provided to preserve the order for those tests.
>>>>>>> Stashed changes

***Default:*** module

<<<<<<< Updated upstream
This option controls the scope of the sort operation.  For example, if the sort bucket is "module", then all tests from the same module will run together.  If the sort bucket is global, than all tests are sorted together.
=======
Java developers will be farmilliar with JUnit. The JUnit package automatically runs test cases in a deterministic, but unpredictable order.  This package can provide similar functionality in pytest several ways.
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
| sort_mode | Definition | 
=======
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

The 'order' marker sets the sort key for the marked test to the provided value.
* The 'item_sort_key' value is required, and can be any value that can be used as a list sort key

Usage Example:
```py
import pytest

@pytest.mark.order(1)
def test_create_the_data():  # always run this first
   ...
@pytest.mark.order(2)
def test_modify_the_data():  # always run this second
   ...
@pytest.mark.order(3)
def test_validate_the_data():  # always run this third
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
>>>>>>> Stashed changes
| --- | --- |
| ordered | (default) pytest_sort will keep the default order of tests. |
| reverse |pytest_sort will reverse the default order of tests. |
| md5 | This mode creates an md5 of each test case id, then sorts on those values.  <br> This runs test cases in a deterministicly shuffled order. |
<<<<<<< Updated upstream
| random | Test cases are shuffled randomly |
| fastest | In each run in "fasttest" mode, the plugin will track the longest execution time for each test case in a file '.pytest-sort'.  <br> At the beginning of a test run, any previously recorded values will be used to sort the tests so that the fastest test runs first.<br>  This is intended for use with "-x" or "--exitfirst"
=======
| random | Test cases are shuffled randomly. Sort Seed is used to control random sorting. |
| fastest | In each run in "fasttest" mode, any previously recorded runtimes in ".pytest_sort" file will be used to sort the fastest tests to run first.  Also, by default, it will record the longest execution time for each test case to that file for future usage.  See [Record Test Runtimes](#record-test-runtimes) |

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

## Sort Seed

Only used in "random" sort mode.  This field allows you to manually set the seed used by random package when sorting tests.

> Tip: Seed is printed in the pytest header

***Command Line:*** `--sort-seed`

***Pytest Config:*** `sort_seed`

***Default:*** A random integer between 0 and 1,000,000 generated at runtime.

## Record Test Runtimes

When this option is enabled, this plugin with collect runtime information for all tests. If the recorded values are higher than values already stored in ".pytest_sort" file, the values in the file are updated.

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

> Runtimes can also be deleted by deleting the '.pytest_sort' file.

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

***Default:*** `.pytest_sort` 
>>>>>>> Stashed changes
