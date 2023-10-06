# Example: Class Variable

_service.py:_
```python3
from typing import ClassVar

class Calulate:
    def __init__(self, start_value: int):
        self._value = start_value

    _increment: ClassVar[int] = 5

    @staticmethod
    def set_increment(increment):
        Calulate._increment = increment

    def next(self):
        self._value += self._increment
        return self._value
```

_test_service.py:_
```python3
import service

def test_calculate_default():
    assert service.Calulate._increment == 5

def test_calculate_next():
    calc = service.Calulate(5)
    assert calc.next() == 10
    assert calc.next() == 15

def test_calculate_next_by_1():
    calc = service.Calulate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7
```

This test module appears to be just fine.
And running the test cases in order succeeds.
But there's a problem here.

The next time that a test case is added that assumes the value of Calculate._increment is 5 will fail.
That's because the test case test_calculate_next_by_1 changed the value of _increment to 1 for the CLASS, not just for the one instance of the class.

## How to find this error?

Running Pytest with the option sort-mode as 'random' will give a very strong chance of finding this error quickly.  Just with these 3 test cases, there's a 66% chance of the test suite failing.  And if one more test case is added that needs _increment to be 5, that raises the chances to 75% chance of finding.

## How to find the cause?

As mentioned before, the example above is drastically oversimplified.
Situations like this are more likely to occur when the project already has hundreds of test cases.
Debugging 3 test cases is not that hard, but debugging 300 or more all at once, is not practical.

Pytest Sort includes options that can help narrow down the list of test cases to examine.

1. Run Pytest with `-vv -x --sort-mode=ordered` and note which test case is the first to fail.
2. Run Pytest with `-vv -x --sort-mode=reverse` and note which test case is the first to fail.
3. Find both test cases in the ordered list in sysout.  The problem is most likely between the two.

Let's try that with the above example.
With ordered mode, none of the test cases fail.
With reverse mode, the first to fail is test_calculate_next.
Looking at the ordered list of test cases in sysout, you can find the test cases that are between test_calculate_next, and the end of the list.
In this simple example, there's only test_calculate_next_by_1.

## How to Fix?

There many valid options for fixing issues like this.  Below are a few I like to use.

### Good

Reset all the variables that the failed test case depends on, before running test case

This can be the simplest to implement, especially if only a couple test cases really depend on the default values.
This is also a useful technique when you can't find the test case causing the problem.

Below, I fixed test_calculate_default by reloading the service module before running the test.
And I fixed test_calculate_next by setting a known value in the class variable before testing.

```python3
import importlib
import service

def test_calculate_default():
    importlib.reload(service)  # reload default values before testing
    assert service.Calulate._increment == 5

def test_calculate_next():
    service.Calulate._increment = 3  # set to known value before testing
    calc = service.Calulate(5)
    assert calc.next() == 8
    assert calc.next() == 11

def test_calculate_next_by_1():
    calc = service.Calulate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7

```

### Better

Reset all variables to defaults before every test case.

This is a little more relyable because it allows all test cases to assume we are starting with default values.
However, you must remember to reload the modules in ever test module.

Below I fixed the tests by adding a Pytest Fixture with autouse=True.
The Fixture will then run before each test case, resetting app module with default values.

```python3
import importlib
import pytest
import service

@pytest.fixture(autouse=True)  # Fixture to reset service module
def _reload_service():
    importlib.reload(service)

def test_calculate_default():
    assert service.Calulate._increment == 5

def test_calculate_next():
    calc = service.Calulate(5)
    assert calc.next() == 10
    assert calc.next() == 15

def test_calculate_next_by_1():
    calc = service.Calulate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7
```

### Best

At the end of any test case that changes application state data, reset the data.

This is the ideal way to prevent these issues.
If each test case cleans up after itself, there is no chance of application state leakage.

The best way to implement this kind of cleanup is with a Pytest Fixture.
Fixtures allow you to run the setup the data, then 'yield' execution to the test case.
After the test case is completed, statments after the 'yield' are run to reset the data.
With a Fixture, the setup and reset pattern becomes reusable by other test cases.
It also will run the reset steps even if the test case fails.
Finally there can be perfomance benefits since we don't need to reset the data before every test case.

```python3
import importlib
import pytest
import service

@pytest.fixture()  # Fixture to reset after testing
def reset_after():
    yield
    importlib.reload(service)

def test_calculate_default():
    assert service.Calulate._increment == 5

def test_calculate_next():
    calc = service.Calulate(5)
    assert calc.next() == 10
    assert calc.next() == 15

def test_calculate_next_by_1(reset_after):
    calc = service.Calulate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7
```