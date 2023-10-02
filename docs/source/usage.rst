Usage
=====
  
Ideally, all test cases should be small and independant. And should cleanup any changes to the application state.  
This package provides several options for validating if test cases can really be run independantly and cleanly.

Deterministic but Unpredictable
-------------------------------

Java developers will be farmilliar with JUnit. The JUnit package automatically runs test cases in a deterministic, but unpredictable order.  
This package can provide similar functionality in pytest several ways.

Using sort mode "md5" will produce the same order of tests every time as long as the test case names don't change.

::

    sort_mode="md5"
   
Using sort mode "random" with a fixed sort seed value will produce the same order of tests every time unles the list of test cases is changed (new test case, or name changes)

::

    sort_mode="random"
    sort_seed=100

Random
------

By running in random mode, the test case order will change every time. If a test case fails unexpectedly, you can use the seed from the failed run to determine what order is causing the tests to fail.

::

    sort_mode="random"


Fail Fast
---------

When you have a test suite that includes long running test cases, it can be helpful to delay the longer running test cases till later.  
The 'fastest' mode allows you to track how long different test cases take to run.  Then always run the fastest test cases first, and the slow test cases last.

::

    pytest --exitfirst --sort-mode=fastest

Mutation Testing
----------------

Mutuation testing is slow.  The 'diffcov' mode can help accelerate mutation testing.

The mutuation testing tool 'mutmut' works by modifying the source code, then running pytest to see if any tests catch the change.  
Using 'git diff' and 'coverage.py' the 'diffcov' mode combines the differences detected by Git with the coverage information recorded by coverage.py to prioritize test cases.  
That way the test cases most likely to catch the change are run as early as possible.

Steps to use 'diffcov' mode:
1. Run pytest with coverage and context.  This records the coverage for each test case as a separate context.

::

    pytest --cov= --cov-context=test

2. Run mutmut with runner options.

::

    mutmut run --runner "pytest --exitfirst --assert=plain --sort-mode=diffcov"

-------------

You can also combine with 'fastest' to run tests with same coverage from fastest to slowest::

    pytest --cov= --cov-context=test --sort-mode=fastest
    mutmut run --runner "pytest --exitfirst --assert=plain --sort-bucket-mode=diffcov --sort-bucket=function --sort-mode=fastest"

