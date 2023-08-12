![python>=3.8](https://img.shields.io/badge/python->=3.8-blue)

# Project description

pytest-sort is a pytest plugin to automatically change the execution order of test cases.  Changing the order of execution can help find test cases that only succeed because of a favorable state.

This plugin provides several options for controlling how the test cases are reordered.

# Quick Start

Installation:

```
pip install pytest-sort --upgrade
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

# Usage

Ideally, all test cases should be small and independant.  This package provides several options for validating if test cases can really be run independantly, or if running them in a specific order is required.

## Deterministic but Unpredictable

The Junit package automatically runs test cases in a deterministic, but unpredictable order.  This package can provide similar functionality in pytest several ways.

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


# Options

## Sort Mode

This option controlls how the order is modified within each bucket.

This option must be set to something other than "none" to enable pytest_sort plugin.

***Command Line:*** `--sort-mode`

***Pytest Config:*** `sort_mode`

***Default:*** `none`

| Option | Definition | 
| --- | --- |
| none | pytest_sort will not modify the sort order.  This option disables pytest_sort. |
| md5 | This mode creates an md5 of each test case id, then sorts on those values.  <br> This runs test cases in a deterministicly shuffled order. |
| random | Test cases are shuffled randomly |
| fastest | In each run in "fasttest" mode, the plugin will track the longest execution time for each test case in a file ".pytest-sort".  <br> At the beginning of a test run, any previously recorded values will be used to sort the tests so that the fastest test runs first.

## Sort Bucket

Sort test order within specified test buckets.

For example, if the sort bucket is "module", then all tests from the same module will be completed before running tests for the next module.

***Command Line:*** `--sort-bucket`

***Pytest Config:*** `sort_bucket`

***Default:*** `module`

| Option | Definition | 
| --- | --- |
| global | Apply sort to all items together. |
| package | Group together test cases that are in the same package (folder). |
| module | Group together test cases that are in the same module (py file). |
| class | Group together test cases that are members of a class.  <br>All other (non-class) test cases are grouped by module. |
| parent | Group together test cases by their immediate parent. |
| grandparent | Group together test cases by their parent's parent. |

## Sort Seed

Only used in "random" sort mode.  This field allows you to manually set the seed used by random package when sorting tests.

> Tip: Seed is printed in the pytest header

***Command Line:*** `--sort-seed`

***Pytest Config:*** `sort_seed`

***Default:*** A random integer between 0 and 1,000,000 generated at runtime.

## Record Test Runtimes

This option enables or disables pytest_sort to record test case runtimes.  These runtimes are used when sort mode is "fastest".  When sort mode is "fastest" recording is enabled by default, otherwise this is disabled by default.

***Command Line:*** `--sort-record-times/--sort-no-record-times`

***Pytest Config:*** `sort_record_times`

***Default:*** false 

| Option | Definition |
| --- | --- |
| `--sort-record-times`<br>`sort_record_times=true` | Record test case runtime statistics |
| `--sort-no-record-times`<br>`sort_record_times=false` | Disable recording runtime statistics in "fastest" mode |

## Reset Recorded Test Runtimes

Clear all recorded runtimes before sorting the next test.

When recording runtimes, only the highest runtime values for each test case are retained.  After significant changes to test cases that can change how fast they run, it is advisable to reset the runtimes.  This can help maintain more accurate sorting in "fastest" mode.

***Command Line:*** `--sort-reset-times`

***Pytest Config:*** N/A

## Report Recorded Test Runtimes

At the end of the test run, print out the currently saved test runtimes.

***Command Line:*** `--sort-reset-times`

***Pytest Config:*** N/A
