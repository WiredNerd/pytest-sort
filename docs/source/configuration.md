# Configuration

## How it Works

Pytest gathers a list of test cases to be executed, by default it orders test cases from top to bottom of each file.
This plugin takes that list and creates two sort keys.  The first is a sort key for each bucket, and the second is a sort key for each test.
It then sorts the list of test cases using the two sort keys.

Bucket is simply a group of test cases.  Depending on the situation it can be better to keep test cases grouped together.
For example, if the test suite includes fixtures with a scope of module, it would be best to use a bucket type of module, class, or parent.
This is because pytest will create that fixture every time testing enters the module, and destroy it every time testing leaves the module.

You can also separately control the sorting method for buckets and for test cases.
For example, if you wanted to always run the modules in order provided by pytest, but wanted to randomize test order within each module.
This can be achieved by setting the Sort Mode to 'random', and the Bucket Sort Mode to 'ordered'.


## Options

For all options, the priority of options is:

1. Pytest Markers (closest to the test case)
2. Command Line Option
3. Pytest Config File
4. Default values

### Sort Mode

This option controls how the order is modified within each bucket.

**Command Line:** ``--sort-mode``

**Pytest Config:** ``sort_mode``

**Default:** ``ordered``

:::{list-table}
:header-rows: 1
:align: left

* - Option
  - Definition
* - ``ordered``
  - (default) pytest_sort will keep the default order of tests.
* - ``reverse``
  - pytest_sort will reverse the default order of tests.
* - ``md5``
  - This mode creates an md5 of each test case id, then sorts on those values.
    This runs test cases in a deterministically shuffled order.
* - ``random``
  - Test cases are shuffled randomly. Sort Seed is used to control random sorting.
* - ``fastest``
  - In each run in "fastest" mode, any previously recorded run times in ".pytest_sort_data" file will be used to sort the fastest tests to run first.
    Also, by default, it will record the longest execution time for each test case to that file for future usage.
    See [Record Test Run Times](#record-test-run-times)
* - ``diffcov``
  - Uses 'git diff' and data from 'coverage.py' to determine which test cases likely cover the changed lines of code, and runs them first. 
  See [Diff Coverage](mutation_testing.md#diff-coverage) for usage example.
* - ``mutcov``
  - Uses environment variables from the Mutation Test tool and data from 'coverage.py' to determine which test cases likely cover the mutated lines of code, and runs them first.
  See [Mutation Coverage](mutation_testing.md#mutation-coverage) for usage example.
:::


### Sort Bucket

Sort test order within specified test buckets.

For example, if the sort bucket is "module", then all tests from the same module will be completed before running tests for the next module.

**Command Line:** ``--sort-bucket``

**Pytest Config:** ``sort_bucket``

**Default:** ``parent``

:::{list-table}
:header-rows: 1
:align: left

* - Option
  - Definition
* - ``session``
  - Apply sort to all items together.
* - ``package``
  - Group together test cases that are in the same package (folder).
* - ``module``
  - Group together test cases that are in the same module (py file).
* - ``class``
  - Group together test cases that are members of a class.  <br>All other (non-class) test cases are grouped by module.
* - ``function``
  - Each test function is assigned a separate bucket.
* - ``parent``
  - Group together test cases by their immediate parent.
* - ``grandparent``
  - Group together test cases by their parent's parent.
:::

:::{note}
If you have fixtures with a scope other than function, it may be best to use sort bucket setting with the same or smaller scope.
Otherwise, fixtures may be destroyed and recreated more than expected.

For example: If sort bucket is "package" and fixture scope is "module", Pytest may setup the fixture every time the testing enters the module, and teardown each time testing leaves the module.

The pytest option ``--setup-show`` can reveal when fixtures are created and destroyed.
:::

### Sort Bucket Mode

This option controls how the order is modified within each bucket.

**Command Line:** ``--sort-bucket-mode``

**Pytest Config:** ``sort_bucket_mode``

**Default:** ``sort_mode``

:::{list-table}
:header-rows: 1
:align: left

* - Option
  - Definition
* - ``sort_mode``
  - (default) Use the same sort mode for buckets as used for tests.  See [Sort Mode](#sort-mode)
* - ``ordered``
  - pytest_sort will keep the default order of buckets.
* - ``reverse``
  - pytest_sort will reverse the default order of buckets.
* - ``md5``
  - This mode creates an md5 of each bucket's id, then sorts on those values.
* - ``random``
  - Buckets are shuffled randomly. Sort Seed is used to control random sorting.
* - ``fastest``
  - The total of all run times for tests in the bucket is used as the sort key for the bucket.
* - ``diffcov``
  - Uses 'git diff' and data from 'coverage.py' to determine which test cases likely cover the changed lines of code, and runs them first.
  See [Diff Coverage](mutation_testing.md#diff-coverage) for usage example.
* - ``mutcov``
  - Uses environment variables from the Mutation Test tool and data from 'coverage.py' to determine which test cases likely cover the mutated lines of code, and runs them first.
  See [Mutation Coverage](mutation_testing.md#mutation-coverage) for usage example.
:::

### Sort Seed

Only used in "random" sort mode.  This field allows you to manually set the seed used by random package when sorting tests.

:::{tip}
Seed is printed in the pytest header
:::

**Command Line:** ``--sort-seed``

**Pytest Config:** ``sort_seed``

**Default:** A random integer between 0 and 1,000,000 generated at runtime.

### Record Test Run Times

When this option is enabled, this plugin with collect runtime information for all tests.
If the recorded values are higher than values already stored in ".pytest_sort_data" file, the values in the file are updated.

When Sort Mode or Bucket Sort Mode is 'fastest', this option is enabled by default.

For any other Sort Mode, this option is disabled by default.

**Command Line:** ``--sort-record-times/--sort-no-record-times``

**Pytest Config:** ``sort_record_times``

**Default:** ``false`` 

:::{list-table}
:header-rows: 1
:align: left

* - Command Line
  - Pytest Config
  - Definition
* - ``--sort-record-times`` 
  - ``sort_record_times=true``
  - Enable recording the maximum test case run times.
* - ``--sort-no-record-times``
  - ``sort_record_times=false``
  - Disable recording test case run times.
:::

### Reset Recorded Test Run Times

Clear all recorded run times before sorting and running the next test.

When recording run times, only the highest runtime values for each test case are retained.
After significant changes to test cases that can change how fast they run, it is advisable to reset the run times.
This can help maintain more accurate sorting in "fastest" mode.

:::{tip}
Run times can also be deleted by deleting the '.pytest_sort_data' file.
:::

**Command Line:** ``--sort-reset-times``

**Pytest Config:** N/A

### Report Recorded Test Run Times

At the end of the test run, print out the currently saved test run times.

**Command Line:** ``--sort-reset-times``

**Pytest Config:** N/A

### Recorded Test Run Times Data File

Change the location and/or name of the data file used to store the test run times.

**Command Line:** ``--sort-datafile``

**Pytest Config:** ``sort_datafile``

**Default:** ``.pytest_sort_data``

## Pytest Markers

What if there are some test cases that NEED to run in a particular order?
For example, you want to test a multi-step workflow, and have it organized into a sequence of test cases.

For this Pytest Sort provides Pytest Markers to keep specific test cases in order regardless of the options in the config files or command line.
In cases like this, my recommendation is to group the test cases that must be kept together into a single class, then decorate that class with `@pytest.mark.sort("ordered")`

### sort

```python3
sort(mode: str, bucket: str = "self")
```


The 'sort' marker allows you to change the sort settings for the marked module or class.
* 'mode' argument is required, and changes the [Sort Mode](#sort-mode) setting for all tests within the marked module or class.
* 'bucket' argument is optional.  By default, the sort marker will set the bucket for all tests in the marked scope to be the marked module or class.
But any other valid [Sort Bucket](#sort-bucket) can be set instead.

Usage Examples:
```python3
import pytest

pytestmark = pytest.mark.sort("random", bucket="package")

def test_that_cba_works():  # This test case is grouped with other tests in the package bucket, and sorted randomly.
...

@pytest.mark.sort("ordered")
class TestClassAbc:
def test_that_abc_works(self): # This test case is grouped with other tests in class TestClassAbc and kept in order listed.
    ...
```


### order
```python3
order(item_sort_key: Any)
```

The 'order' marker sets the sort key for the marked test, class, or module to the provided value.
* The 'sort_key' value is required, and can be any value that can be used as a list sort key

When used to mark a test function, the sort key for that item is set to the provided value.

When used to mark a test Class or Module, the Class or Module is used as a bucket for all test within it, and the sort key for the bucket is set to the provided value.

Usage Example:

```python3
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
