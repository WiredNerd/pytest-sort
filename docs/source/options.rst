
Options
=======

For all options, the priority of options is:

1. Pytest Markers (closest to the test case)
2. Command Line Option
3. Pytest Config Option
4. Default values

Sort Mode
---------

This option controlls how the order is modified within each bucket.

**Command Line:** ``--sort-mode``

**Pytest Config:** ``sort_mode``

**Default:** ``ordered``

.. list-table:: 
   :header-rows: 1

   * - Option
     - Definition
   * - ``ordered``
     - (default) pytest_sort will keep the default order of tests.
   * - ``reverse``
     - pytest_sort will reverse the default order of tests.
   * - ``md5``
     - This mode creates an md5 of each test case id, then sorts on those values.
       This runs test cases in a deterministicly shuffled order.
   * - ``random``
     - Test cases are shuffled randomly. Sort Seed is used to control random sorting.
   * - ``fastest``
     - In each run in "fastest" mode, any previously recorded runtimes in ".pytest_sort_data" file will be used to sort the fastest tests to run first.
       Also, by default, it will record the longest execution time for each test case to that file for future usage.
       See [Record Test Runtimes](#record-test-runtimes)
   * - ``diffcov``
     - Uses 'git diff' and data from 'coverage.py' to determine which test cases likey cover the changed lines of code, and runs them first. 

Sort Bucket
-----------

Sort test order within specified test buckets.

For example, if the sort bucket is "module", then all tests from the same module will be completed before running tests for the next module.

**Command Line:** ``--sort-bucket``

**Pytest Config:** ``sort_bucket``

**Default:** ``parent``

.. list-table:: 
   :header-rows: 1

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

.. note:: 

    If you have fixtures with a scope other than function, it may be best to use sort bucket setting with the same or smaller scope.
    Otherwise, fixtures may be destroyed and recreated more than expected.
    
    For example: If sort bucket is "package" and fixture scope is "module", Pytest may setup the fixture every time the testing enters the module, and teardown each time testing leaves the module.

    The pytest option ``--setup-show`` can reveal when fixtures are created and destroyed.

Bucket Sort Mode
----------------

This option controlls how the order is modified within each bucket.

**Command Line:** ``--sort-bucket-mode``

**Pytest Config:** ``sort_bucket_mode```

**Default:** ``sort_mode```

.. list-table:: 
   :header-rows: 1

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
     - The total of all runtimes for tests in the bucket is used as the sort key for the bucket.
   * - ``diffcov``
     - Uses 'git diff' and data from 'coverage.py' to determine which test cases likey cover the changed lines of code, and runs them first.

Sort Seed
---------

Only used in "random" sort mode.  This field allows you to manually set the seed used by random package when sorting tests.

.. tip:: Seed is printed in the pytest header

**Command Line:** ``--sort-seed``

**Pytest Config:** ``sort_seed```

**Default:** A random integer between 0 and 1,000,000 generated at runtime.

Record Test Runtimes
--------------------

When this option is enabled, this plugin with collect runtime information for all tests. 
If the recorded values are higher than values already stored in ".pytest_sort_data" file, the values in the file are updated.

When Sort Mode or Bucket Sort Mode is 'fastest', this option is enabled by default.

For any other Sort Mode, this option is disabled by default.

**Command Line:** ``--sort-record-times/--sort-no-record-times``

**Pytest Config:** ``sort_record_times``

**Default:** ``false`` 

.. list-table:: 
   :header-rows: 1

   * - Command Line
     - Pytest Config
     - Definition
   * - ``--sort-record-times`` 
     - ``sort_record_times=true``
     - Enable recording the maximum test case runtimes.
   * - ``--sort-no-record-times``
     - ``sort_record_times=false``
     - Disable recording test case runtimes.

Reset Recorded Test Runtimes
----------------------------

Clear all recorded runtimes before sorting and running the next test.

When recording runtimes, only the highest runtime values for each test case are retained.  
After significant changes to test cases that can change how fast they run, it is advisable to reset the runtimes.  
This can help maintain more accurate sorting in "fastest" mode.

.. tip:: Runtimes can also be deleted by deleting the '.pytest_sort_data' file.

**Command Line:** ``--sort-reset-times``

**Pytest Config:** N/A

Report Recorded Test Runtimes
-----------------------------

At the end of the test run, print out the currently saved test runtimes.

**Command Line:** ``--sort-reset-times``

**Pytest Config:** N/A

Recorded Test Runtimes Datafile
-------------------------------

Change the location and/or name of the datafile used to store the test runtimes.

**Command Line:** ``--sort-datafile``

**Pytest Config:** ``sort_datafile``

**Default:** ``.pytest_sort_data``

