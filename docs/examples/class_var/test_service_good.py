import importlib

from class_var import service


def test_calculate_default():
    importlib.reload(service)  # reload default values before testing
    assert service.Calculate._increment == 5


def test_calculate_next():
    service.Calculate._increment = 3  # set to known value before testing
    calc = service.Calculate(5)
    assert calc.next() == 8
    assert calc.next() == 11


def test_calculate_next_by_1():
    calc = service.Calculate(5)
    calc.set_increment(1)
    assert calc.next() == 6
    assert calc.next() == 7
