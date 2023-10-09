# Usage

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

Once you have found settings that best fit your needs, save them in your [pytest configuration file](https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats)

### New Project

When starting a new project, I recommend adding the following options to your [pytest configuration file](https://docs.pytest.org/en/stable/reference/customize.html#configuration-file-formats):
```
sort_mode = random
sort_bucket = session
```

As you develop your test suite:
* If you need to create fixtures with scope of module or package, consider changing the sort_bucket setting to match.  See [sort-bucket](project:configuration.md#sort-bucket) for details.
* If you are adding test cases that must be run in a specific order.  Try grouping them in a class, and decorating the class with `@pytest.mark.sort("ordered")`

## Problem Solving

### Finding State Leaks

1. Run Pytest with `-vv -x --sort-mode=ordered` and note which test case is the first to fail.
2. Run Pytest with `-vv -x --sort-mode=reverse` and note which test case is the first to fail.
3. Find both test cases in the ordered list in sysout.  The problem is most likely between the two.
4. Walkthrough and/or Debug the test cases that might be a problem.
Look specifically for any variables that are changed by the test case.
If those variables are retained after the test case, they are likely the cause.
See [The Problem](project:problem.md) for examples of common causes of Application State Leaks.

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

Java developers may be farmilliar with JUnit. The JUnit package automatically runs test cases in a deterministic, but unpredictable order.  
This package can provide similar functionality in Pytest.

Using `--sort-mode=md5` will produce the same order of tests every time as long as the test case names don't change.

### Fail Fast

When you have a test suite that includes long running test cases, it can be helpful to delay the longer running test cases till later.  
Using `--sort-mode=fastest` mode allows you to track how long different test cases take to run.  Then always run the fastest test cases first, and the slow test cases last.

### Mutation Testing

Mutation testing is slow.  But Pytest Sort has a couple of options that can help.

#### Mutation Testing with Fastest

If your test suite has some slow test cases, accelerating mutation testing could be as simple as using `--sort-mode=fastest`.

Pytest Sort will track the execution times of the test cases, and prioritize the faster ones to run first.
During mutation testing, test's for each mutation should stop as soon as one test case detects it.
Therefore, by running the slow test cases last, they should only be executed if no fast test case detects the mutation.

#### Mutation Testing with Diffcov

If you are using a mutation testing tool like [Mutmut](https://mutmut.readthedocs.io) that changes the source code.
And you are using Git to track source code changes.
The 'diffcov' mode may help.

The mutuation testing tools like Mutmut work by modifying the source code, then running pytest to see if any tests catch the change.
Using 'git diff' and 'coverage.py' the 'diffcov' mode combines the differences detected by Git with the coverage information recorded by coverage.py to prioritize test cases.
That way the test cases most likely to catch the change are run first.

Steps to use 'diffcov' mode:
1. Run pytest with coverage and context enabled.  This records the coverage for each test case as a separate context.

    Example: `pytest --cov=src --cov-context=test`

2. Run mutmut with runner options.

    `mutmut run --runner "pytest --exitfirst --assert=plain --sort-mode=diffcov"`

#### Combining Options

If you are able to use 'diffcov' and have some slow test cases, you can also try combining the options.

In this example, we are sirting first by diffcov, then by fastest:
```
pytest --cov=src --cov-context=test --sort-mode=fastest
mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=diffcov --sort-bucket=function --sort-mode=fastest"
```

