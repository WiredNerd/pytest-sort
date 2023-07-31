import time

from pytest_sort import plugin


def test_dummy3():
    time.sleep(0.30)
    assert plugin.create_bucket_key is not None
    pass


def test_dummy1():
    time.sleep(0.05)
    pass


def test_dummy2():
    time.sleep(0.25)
    pass
