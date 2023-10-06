# The Problem

Unit testing in Python can be a real pain.
The extreme flexibility of python can be both a blessing and a curse.
And nothing makes this more apperent than unit testing.

The blessing is some of the super easy to use tools like Pytest's fixtures and Unittest's MagicMock.
Unittest's Patch allows you to replace _anything_ with a mock object.
MagicMock can easily mock any variable or function, including complex objects.
And fixtures allow you to create reusable Patches or other testing objects, and clean them up after.

The curse is that it's **very** easy to miss resetting things that were changed in the test case.
At the end of the test case, without special cleanup steps, module variables, test module variables, class variables and more may contain artifacts of the test run.  
And, in my experience, it won't cause a problem until two weeks later, while working on unit testing for a completely different module

**UGH**

Let's look at some drastically oversimplified examples to demonstrate how application state leaks occur.

```{toctree}
:titlesonly:
example_env.md
example_class.md
```

## How to Prevent?

Pytest normally runs tests in order, from top to bottom, every time.
Becasue of this, it is easy for issues like the ones in the examples to go unnoticed for a long time.
However, Pytest Sort has options to help find these issues faster.

In your [Pytest Configuration File](https://docs.pytest.org/en/7.4.x/reference/customize.html#configuration-file-formats), start with the following setting `sort_mode = random`.
This will trigger Pytest Sort to shuffle the test cases randomly each time.
If a test case is leaving application state changes behind, you are more likely to see the surprise failures quickly.

As needed, you can also adjust the sort_bucket setting to group test cases together appropriately.  If you use fixtures with a scope other than 'function', it may be best for the sort_bucket setting to match.

If you are looking for something that is a little more consistent between runs, try `sort_mode = md5`.
With this, the test cases are shuffled, but always in the same order.

See [Pytest Sort Options](project:options.rst)

## Keeping Order

What if there are some test cases that NEED to run in a particular order?
For example, you want to test a multi-step workflow, and have it organized into a sequence of test cases.

For this Pytest Sort provides Pytest Markers to keep specific test cases in order regardless of the options in the config files or command line.
In cases like this, my recommendation is to group the test cases that must be kept together into a single class, then decorate that class with `@pytest.mark.sort("ordered")`

See [Pytest Sort Markers](project:markers.rst)