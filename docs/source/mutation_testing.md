# Mutation Testing

Mutation testing is slow.  But Pytest Sort has a couple of options that can help.

## Fastest First

If your test suite has some slow test cases, accelerating mutation testing could be as simple as using `--sort-mode=fastest`.

Pytest Sort will track the execution times of the test cases, and prioritize the faster ones to run first.
During mutation testing, testing for each mutation should stop as soon as one test case detects it.
Therefore, by running the slow test cases last, they should only be executed if no fast test case detects the mutation.

## Diff Coverage

If you are using a mutation testing tool like [Mutmut](https://mutmut.readthedocs.io) that changes the source code.
And you are using Git to track source code changes.
The 'diffcov' mode may help.

The mutation testing tools like Mutmut work by modifying the source code, then running pytest to see if any tests catch the change.
Using 'git diff' and 'coverage.py' the 'diffcov' mode combines the differences detected by Git with the coverage information recorded by coverage.py to prioritize test cases.
That way the test cases most likely to catch the change are run first.

Steps to use 'diffcov' mode:
1. __Commit your changes to Git!__
2. Run pytest with coverage and context enabled.  This records the coverage for each test case as a separate context.

    Example: `pytest --cov=src --cov-context=test`

3. Run mutmut with runner options.

    `mutmut run --runner "pytest --exitfirst --assert=plain --sort-mode=diffcov"`

## Combining Options

If you are able to use 'diffcov' and have some slow test cases, you can also try combining the options.

In this example, we are sorting first by diffcov, then by fastest:
```
pytest --cov=src --cov-context=test --sort-mode=fastest
mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=diffcov --sort-bucket=function --sort-mode=fastest"
```

