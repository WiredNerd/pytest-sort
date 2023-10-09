# Using Pytest Sort

## Getting Started

### Existing Project

1. Start by running pytest normally and noting how long it takes to run.  
2. Install pytest-sort: `pip install pytest-sort --upgrade`
3. Then run pytest with `--sort-mode=random`
4. Then run with larger bucket sizes:
    1. `--sort-bucket=module`
    2. `--sort-bucket=package`
    3. `--sort-bucket=session`

:::{tip}
On some systems, run `time pytest` to print runtime after completion
:::

Ideally, test suites should be run with `--sort-mode=random --sort-bucket=session`.
But this is not always practical.
* If test cases fail when changing the order, or increasing the bucket size, you may have Application State Leaks.
See [Finding State Leaks](project:#finding-state-leaks) below for help resolving.
* If runtime of the pytest is significantly longer with a larger bucket sizes, you may have fixtures that are being created and destroyed more than expected.  See [sort-bucket](project:configuration.md#sort-bucket) for details.
* If you discover that some test cases really should be run in order, try using [Pytest Markers](project:configuration.md#pytest-markers) 'sort' or 'order' to keep those tests in a set order.

Once you have found settings that best fit your needs, save them in your [Pytest configuration file](https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats)

### New Project

When starting a new project, I recommend adding the following options to your [Pytest configuration file](https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats):
```
sort_mode = random
sort_bucket = session
```

As you develop your test suite:
* If you need to create fixtures with scope of module or package, consider changing the sort_bucket setting to match.  See [sort-bucket](project:configuration.md#sort-bucket) for details.
* If you are adding test cases that must be run in a specific order.  Try grouping them in a class, and decorating the class with `@pytest.mark.sort("ordered")`.  See [Pytest Markers](project:configuration.md#pytest-markers) for more options.

## Problem Solving

### Finding State Leaks

1. Run Pytest with `-vv -x --sort-mode=ordered` and note which test case is the first to fail.
2. Run Pytest with `-vv -x --sort-mode=reverse` and note which test case is the first to fail.
3. Find both test cases in the ordered list in sysout.  The problem is most likely between the two.
4. Walkthrough and/or Debug the test cases that might be a problem.
Look specifically for any variables that are changed by the test case.
If those variables are retained after the test case, they are likely the cause.
See [Application State Leaks](project:app_state_leaks.md) for examples of common causes.

### Pytest Sometimes Fails

When using Random sort mode, pytest can sometimes find a lucky order where the testcases pass.
Then later find an unlucky order where they don't.

The output of pytest should include a sort-seed value that was used.  Example:
```
$ pytest --sort-mode=random
============================================================================ ============================================================================
platform win32 -- Python 3.11.5, pytest-7.4.2, pluggy-1.3.0
pytest-sort:
  sort-mode: random
  sort-bucket: parent
  sort-seed: 332925
```

If you specify the sort seed value from the test run that failed, you should get the exact same order of test cases.
This should help you to debug and find the cause.

I also recommend following the steps in [Finding State Leaks](project:#finding-state-leaks)

## More Sort Patterns

### Deterministic Shuffle

Java developers may be familiar with JUnit. The JUnit package automatically runs test cases in a deterministic, but unpredictable order.
This package can provide similar functionality in Pytest.

Using `--sort-mode=md5` will produce the same order of tests every time as long as the test case names don't change.

### Fail Fast

When you have a test suite that includes long running test cases, it can be helpful to delay the longer running test cases till later.
Using `--sort-mode=fastest` mode allows you to track how long different test cases take to run.  Then always run the fastest test cases first, and the slow test cases last.

### Test Changed Code

If you are using Git to track source code changes, Pytest Sort can use information from Git and [pytest-cov](https://pytest-cov.readthedocs.io/) to prioritize test cases.

Example: `pytest --cov=src --cov-context=test --sort-mode=diffcov --exitfirst`

* `--cov=src` tells pytest-cov to generate coverage data for everything in the 'src' folder.
* `--cov-context=test` tells pystest-cov to store the test case ID in the coverage data for each test.
* `--sort-mode=diffcov` tells pytest-sort to run `git diff` to find the lines of code that changed since last commit.
    It then finds test cases that have coverage for those changed lines of code, and runs them first.
* `--exitfirst` tells pytest to exit after the first test case failure.

:::{tip}
Run once before you start making changes to collect coverage information.
:::

### Combining Options

Pytest Sort allows you to set different sort options for buckets and tests.

For example, this line will group test cases by module, run the modules in order, but randomize the tests within each module.

```
pytest --sort-mode=random --sort-bucket=module --sort-bucket-mode=ordered
```

See [Sort Bucket Mode](project:configuration.md#sort-bucket-mode) for more details.

