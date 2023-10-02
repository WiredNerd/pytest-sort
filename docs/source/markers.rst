Pytest Markers
==============

sort
----

::

    sort(mode: str, bucket: str = "self")


The 'sort' marker allows you to change the sort settings for the marked module or class. 
* 'mode' argument is required, and changes the [Sort Mode](#sort-mode) setting for all tests within the marked module or class.
* 'bucket' argument is optional.  By default, the sort marker will set the bucket for all tests in the marked scope to be the marked module or class.  
But any other valid [Sort Bucket](#sort-bucket) can be set instead.

Usage Examples::

    import pytest

    pytestmark = pytest.mark.sort("random", bucket="package")

    def test_that_cba_works():  # This test case is grouped with other tests in the package bucket, and sorted randomly.
    ...

    @pytest.mark.sort("ordered")
    class TestClassAbc:
    def test_that_abc_works(self): # This test case is grouped with other tests in class TestClassAbc and kept in order listed.
        ...

order
-----

::

    order(item_sort_key: Any)


The 'order' marker sets the sort key for the marked test, class, or module to the provided value.
* The 'sort_key' value is required, and can be any value that can be used as a list sort key

When used to mark a test function, the sort key for that item is set to the priovided value.

When used to mark a test Class or Module, the Class or Module is used as a bucket for all test within it, and the sort key for the bucket is set to the provided value.

Usage Example::

    import pytest

    pytestmark = pytest.mark.order("my_tests")

    @pytest.mark.order("test_group_1")
    class TestClass:
        @pytest.mark.order(1)
        def test_create_the_data():  # bucket_key="test_group_1", item_key=1
            ...
        @pytest.mark.order(2)
        def test_modify_the_data():  # bucket_key="test_group_1", item_key=2
            ...
        @pytest.mark.order(3)
        def test_validate_the_data():  # bucket_key="test_group_1", item_key=3
            ...

    @pytest.mark.order("ZZZ")
        def test_delete_the_data():  # bucket_key="my_tests", item_key="ZZZ"
            ...
