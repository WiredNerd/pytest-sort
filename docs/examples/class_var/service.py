from typing import ClassVar


class Calculate:
    def __init__(self, start_value: int):
        self._value = start_value

    _increment: ClassVar[int] = 5

    @staticmethod
    def set_increment(increment):
        Calculate._increment = increment

    def next(self):
        self._value += self._increment
        return self._value
