import time

from pytest_sort import core
import pytest

pytest.fixture()


def test_dummy3():
    time.sleep(0.30)
    assert core.create_bucket_key is None


def test_dummy1():
    l = [
        (1, "", 0),
        (1, "", 1),
        (1, "", 2),
        (1, "A", 0),
        (1, "A", 0),
        (1, "A", 0),
        (1, "a", 0),
        (1, "a", 1),
        (1, "a", 1),
        (1, "0", 0),
    ]
    l.sort()
    print(l)
    time.sleep(0.05)


def test_dummy2():
    time.sleep(0.25)
