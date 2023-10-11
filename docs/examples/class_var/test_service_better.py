import importlib

import pytest

from class_var import service


@pytest.fixture(autouse=True)  # Fixture to reset service module
def _reload_service():
    importlib.reload(service)


def test_calculate_default():
    assert service.Calculate._increment == 5


def test_calculate_next():
    calc = service.Calculate(5)
    assert calc.next() == 10
    assert calc.next() == 15


def test_calculate_next_by_1():
    calc = service.Calculate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7
