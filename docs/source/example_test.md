# Example: Test Variable

I first encountered this when mocking a service call that returns pages of data with a next key.  Here's a simplified example

_core.py:_
```python3
from test_var.service import get_values

def get_all_values():
    response = get_values()
    values = response["values"]

    while response["next"]:
        response = get_values(response["next"])
        values.extend(response["values"])
    
    return values
```

_test_core.py:_
```python3
from unittest import mock
from test_var import core

response_1 = {"next": "2", "values": [1]}
response_2 = {"next": "3", "values": [2]}
response_3 = {"next": "", "values": [3]}

@mock.patch("test_var.core.get_values")
def test_get_all_values_no_next(get_values):
    get_values.return_value = response_3
    assert core.get_all_values() == [3]

@mock.patch("test_var.core.get_values")
def test_get_all_values_one_loop(get_values):
    get_values.side_effect = [response_2, response_3]
    assert core.get_all_values() == [2, 3]

@mock.patch("test_var.core.get_values")
def test_get_all_values_two_loops(get_values):
    get_values.side_effect = [response_1, response_2, response_3]
    assert core.get_all_values() == [1, 2, 3]
```

At first, this test setup looks fine.  If you run each test case one at a time, they all pass.
However, if you run them together, test_get_all_values_two_loops fails with an error like:

`AssertionError: assert [1, 2, 3, 3] == [1, 2, 3]`

Where'd the extra '3' come from?

## How to find the cause?

Pytest Sort includes options that can help narrow down the list of test cases to examine.

1. Run Pytest with `-vv -x --sort-mode=ordered` and note which test case is the first to fail.
2. Run Pytest with `-vv -x --sort-mode=reverse` and note which test case is the first to fail.
3. Find both test cases in the ordered list in sysout.  The problem is most likely between the two.

Let's try that with the above example.
With ordered mode, test_get_all_values_two_loops is the first to fail.
With reverse mode, none of the test cases fail.
This narrows it down to either test_get_all_values_no_next or test_get_all_values_one_loop is changing something that breaks test_get_all_values_two_loops.

Since there's only 3 test cases in this simple example, that didn't help much.
But, situations like this are more likely to occur when the project already has hundreds of test cases.
Debugging 2 test cases is not that hard, but debugging 300 or more all at once, is not practical.

## Shall we Debug?

Let's put a break point on the lines `values = response["values"]` and `values.extend(response["values"])` in `get_all_values` to see what responses we're working with.
And let's debug all three test cases together running in order

1. The first pause is in 'test_get_all_values_no_next'.
    * The value of `response` is `{'next': '', 'values': [3]}` - OK
2. The next pause is in 'test_get_all_values_one_loop'.
    * The value of `response` is `{'next': '3', 'values': [2]}` - OK
3. The next pause is the loop of 'get_all_values'.
    * The value of `response` is `{'next': '', 'values': [3]}` - OK
4. The next pause is in 'test_get_all_values_two_loops'.
    * The value of `response` is `{'next': '2', 'values': [1]}` - OK
5. The next pause is the loop of 'get_all_values'.
    * The value of `response` is `{'next': '3', 'values': [2, 3]}` - NOT OK

That was supposed to be the value of 'response_2', why is it different?
Well, it's because get_all_values is collecting the values efficiently.
It's taking the response from the first call, and extending it with response from the second call, etc.
So, during test_get_all_values_one_loop, get_all_values is taking the 'values' list from response_2, and extending it with the 'values' list from response_3.

The result of that is, at the end of the second test case, the test variable response_2 contains `{'next': '3', 'values': [2, 3]}`.

## How to Fix?

Well, you could recreate response_1, response_2, and response_3 inside each test case.
But we are already trying to reuse those values, so let's create a fixture instead.
This fixture will create the three test objects from scratch before each test.
You could alternately create 3 fixtures, one for each response.  
That would save execution time, especially if you were loading data form a file.

_test_core.py:_
```python3
from unittest import mock
import pytest
from test_var import core

@pytest.fixture()
def responses():
    return (
        {"next": "2", "values": [1]},
        {"next": "3", "values": [2]},
        {"next": "", "values": [3]},
    )

@mock.patch("test_var.core.get_values")
def test_get_all_values_no_next(get_values, responses):
    get_values.return_value = responses[2]
    assert core.get_all_values() == [3]

@mock.patch("test_var.core.get_values")
def test_get_all_values_one_loop(get_values, responses):
    get_values.side_effect = [responses[1], responses[2]]
    assert core.get_all_values() == [2, 3]

@mock.patch("test_var.core.get_values")
def test_get_all_values_two_loops(get_values, responses):
    get_values.side_effect = [responses[0], responses[1], responses[2]]
    assert core.get_all_values() == [1, 2, 3]
```