# Application State Leaks

Unit testing in Python can be a real pain.
The extreme flexibility of python can be both a blessing and a curse.
And nothing makes this more apparent than unit testing.

The blessing is some of the super easy to use tools like Pytest's fixtures and Unittest's MagicMock.
Unittest's Patch allows you to replace _anything_ with a mock object.
MagicMock can easily mock any variable or function, including complex objects.
And fixtures allow you to create reusable Patches or other testing objects, and clean them up after.

The curse is that it's **very** easy to miss resetting things that were changed in the test case.
At the end of the test case, without special cleanup steps, module variables, test module variables, class variables and more may contain artifacts of the test run.  
And, in my experience, it won't cause a problem until two weeks later, while working on unit testing for a completely different module

**UGH**

Let's look at some drastically oversimplified examples to demonstrate how Application State Leaks occur.

```{toctree}
:titlesonly:
example_env.md
example_class.md
example_test.md
```

## How to Prevent?

Pytest normally runs tests in order, from top to bottom, every time.
Because of this, it is easy for issues like the ones in the examples to go unnoticed for a long time.
However, Pytest Sort has options to help find these issues faster.

See [Using Pytest Sort](project:usage.md)

