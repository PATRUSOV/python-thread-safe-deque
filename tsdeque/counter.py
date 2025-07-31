class Counter:
    def __init__(self) -> None:
        self._value = 0

    def incr(self) -> None:
        self._value += 1

    def decr(self) -> None:
        self._value -= 1

    def reset(self) -> None:
        self._value = 0

    def is_zero(self) -> bool:
        return self._value == 0

    def value(self) -> int:
        return self._value
