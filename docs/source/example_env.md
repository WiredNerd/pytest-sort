# Example: Module Variable

_app.py:_
```
import os

USERNAME = os.environ.get("DB_USERNAME") or "default"

def get_username():
    return USERNAME
```

_test_app.py:_
```python3
import importlib
import os
from unittest import mock
import app

def test_default_username():
    assert app.USERNAME == "default"

def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
    assert app.USERNAME == "test_user"

def test_get_username():
    assert app.get_username() == "default"
```

At first, this test setup looks fine.  If you run each test case one at a time, they all pass.
However, if you run them together, test_get_username fails with an error like:

`AssertionError: assert 'test_user' == 'default'`

**Why did that fail?!**

## Shall we debug?

_test_app.py:_
```python3
import app
```
This triggers the code in app.py to run.

_app.py:_
```python3
USERNAME = os.environ.get("DB_USERNAME") or "default"
```
Assuming the DB_USERNAME environment variable is unset, USERNAME is populated with "default".

_test_app.py:_
```python3
def test_default_username():
    assert app.USERNAME == "default"
```
This test case does not modify any variables, so no problem here.

_test_app.py:_
```python3
def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
```
This test case starts by temporariliy modifying `os.environ`.  Then, reloading the `app` module.  

_app.py:_
```python3
USERNAME = os.environ.get("DB_USERNAME") or "default"
```
Now USERNAME is assigned the value "test_user"

_test_app.py:_
```python3
    assert app.USERNAME == "test_user"
```
And this passes.  However, this is the place where the problem occurs.

At the end of the test_username test case, app.USERNAME is "test_user", and there's no command telling python to change the variable back to default.

Therefore, the next test case, which needs the value to be default, fails.

_test_app.py:_
```python3
def test_get_username():
    assert app.get_username() == "default"
```
The get_username operation reads app.USERNAME, which is still "test_user".

## Where to Look?

As mentioned before, the example above is drastically oversimplified.
Situations like this are more likely to occur when the project already has hundreds of test cases.
Debugging 3 test cases is not that hard, but debugging 300 or more all at once, is not practical.

Pytest Sort includes options that can help narrow down the list of test cases to examine.

1. Run Pytest with `-vv -x --sort-mode=ordered` and note which test case is the first to fail.
2. Run Pytest with `-vv -x --sort-mode=reverse` and note which test case is the first to fail.
3. Find both test cases in the ordered list in sysout.  The problem is most likely between the two.

Let's try that with the above example.
With ordered mode, the firt to fail is test_get_username.
With reverse mode, the first to fail is test_default_username.
Looking at the ordered list of test cases in sysout, you can find the test cases that are between the two.
In this simple example, there's only test_username.

## How to Fix?

There many valid options for fixing issues like this.  Below are a few I like to use.

### Good

Reset all the variables that the failed test case depends on, before running test case

This can be the simplest to implement, especially if only a couple test cases really depend on the default values.
This is also a useful technique when you can't find the test case causing the problem.

Below, I fixed test_default_username by reloading the app module before running the test.
And I fixed test_get_username by setting a known value in the module variable before testing.

```python3
import importlib
import os
from unittest import mock
import app

def test_default_username():
    importlib.reload(app)  # Reload defaults before Testing
    assert app.USERNAME == "default"

def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
    assert app.USERNAME == "test_user"

def test_get_username():
    app.USERNAME = "example_user"  # Set expected value
    assert app.get_username() == "default"
```

### Better

Reset all variables to defaults before every test case.

This is a little more relyable because it allows all test cases to assume we are starting with default values.
However, you must remember to reload the modules in ever test module.

Below I fixed the tests by adding a Pytest Fixture with autouse=True.
The Fixture will then run before each test case, resetting app module with default values.

```python3
import importlib
import os
from unittest import mock
import pytest
import app

@pytest.fixture(autouse=True)  # Fixture to reset app module
def _reset_data():
    importlib.reload(app)

def test_default_username():
    assert app.USERNAME == "default"

def test_username():
    with mock.patch.dict(os.environ, {"DB_USERNAME": "test_user"}):
        importlib.reload(app)
    assert app.USERNAME == "test_user"

def test_get_username():
    assert app.get_username() == "default"
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
import os
from unittest import mock
import pytest
import app

@pytest.fixture()  # Fixture to set envionment variables, and reset after testing
def enviornment_variables():
    vars = {"DB_USERNAME": "test_user"}
    with mock.patch.dict(os.environ, vars):
        importlib.reload(app)
        yield vars
    importlib.reload(app)

def test_default_username():
    assert app.USERNAME == "default"

def test_username(enviornment_variables):
    assert app.USERNAME == enviornment_variables["DB_USERNAME"]

def test_get_username():
    assert app.get_username() == "default"
```