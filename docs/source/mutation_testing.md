# Mutation Testing

Mutation testing is slow.  But Pytest Sort has a couple of options that can help.

## Fastest First

If your test suite has some slow test cases, accelerating mutation testing could be as simple as using `--sort-mode=fastest`.

Pytest Sort will track the execution times of the test cases, and prioritize the faster ones to run first.
During mutation testing, testing for each mutation should stop as soon as one test case detects it.
Therefore, by running the slow test cases last, they should only be executed if no fast test case detects the mutation.

## Mutation Coverage

If you are using a mutation testing tool like [Poodle](https://poodle.readthedocs.io) that sets environment variables indicating what code was mutated.
The 'mutcov' mode will help.

The mutation testing tools like Poodle work by creating a copy of the source code, modifying the copy, and running pytest against the copy.
In this case, tools like 'git diff' cant reasonably tell what lines changed since the change happened in a temporary location, that may be ignored by git.

The 'mutcov' mode reads environment variables `MUT_SOURCE_FILE`, `MUT_LINENO`, and `MUT_END_LINENO` to identify what changed. Then compares that to data recorded by 'coverage.py' to determine which test cases cover that change.
It moves the test cases most likely to catch the mutation to run first.

Steps to use 'mutcov' mode:
1. Install [pytest-cov](https://pypi.org/project/pytest-cov/) plugin: `pip install pytest-cov`
1. Run pytest with coverage and context enabled.  This records the coverage for each test case as a separate context.

    Example: `pytest --cov=src --cov-context=test`

3. Update Configuration options to add '--sort-mode=mutcov' to the command.  

   See [Poodle Command Line Option](https://poodle.readthedocs.io/en/latest/runners.html#command-line)

   Example: `command_line = "pytest -x --assert=plain -o pythonpath='{PYTHONPATH}' --sort-mode=mutcov"`

4. Run Poodle

    Example: `poodle`

### Additional Options

If you are able to use 'mutcov' and have some slow test cases, you can also try combining the options.

In this example, we are sorting first by mutcov, then by fastest:
```
pytest --cov=src --cov-context=test --sort-mode=fastest
mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=mutcov --sort-bucket=function --sort-mode=fastest"
```

## Diff Coverage

If you are using a mutation testing tool like [Mutmut](https://mutmut.readthedocs.io) that changes the source code.
And you are using Git to track source code changes.
The 'diffcov' mode may help.

The mutation testing tools like Mutmut work by modifying the source code, then running pytest to see if any tests catch the change.
Using 'git diff' and 'coverage.py' the 'diffcov' mode combines the differences detected by Git with the coverage information recorded by coverage.py to prioritize test cases.
That way the test cases most likely to catch the change are run first.

Steps to use 'diffcov' mode:
1. __Commit your changes to Git!__
   There is always a risk with Mutmut of mutations or other artifacts being left behind.  Especially if the application crashes for some reason.
2. Install [pytest-cov](https://pypi.org/project/pytest-cov/) plugin: `pip install pytest-cov`
2. Run pytest with coverage and context enabled.  This records the coverage for each test case as a separate context.

    Example: `pytest --cov=src --cov-context=test`

3. Run mutmut with runner options.

    `mutmut run --runner "pytest --exitfirst --assert=plain --sort-mode=diffcov"`

### Additional Options

If you are able to use 'diffcov' and have some slow test cases, you can also try combining the options.

In this example, we are sorting first by diffcov, then by fastest:
```
pytest --cov=src --cov-context=test --sort-mode=fastest
mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=diffcov --sort-bucket=function --sort-mode=fastest"
```
