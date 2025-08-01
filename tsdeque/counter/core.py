import math

from tsdeque.counter.threshold import Threshold
from tsdeque.counter.exceptions import LowThresholdError, HighThresholdError
from tsdeque.counter.nulldevent import _NULL_DEVENT


class Counter:
    def __init__(
        self,
        value: int = 0,
        low_trashold: Threshold = Threshold(
            value=-math.inf,
            event=_NULL_DEVENT,
        ),
        high_trashold: Threshold = Threshold(
            value=math.inf,
            event=_NULL_DEVENT,
        ),
    ) -> None:
        self._min_event = low_trashold.event
        self._max_event = high_trashold.event

        self._min = low_trashold.value
        self._max = high_trashold.value

        if not self._max > self._min:
            raise ValueError("Верхняя граница должна быть меньше нижней.")

        self._set_value(value)

    def _set_value(self, value: int):
        self._value = value

        if self._value < self._min:
            raise LowThresholdError()
        elif self._value > self._max:
            raise HighThresholdError()

        if self._value == self._min:
            self._min_event.set()
            self._max_event.unset()
        elif self._value == self._max:
            self._max_event.set()
            self._min_event.unset()
        else:
            self._max_event.unset()
            self._min_event.unset()

    def incr(self) -> None:
        if self.is_max():
            raise HighThresholdError()

        self._value += 1
        self._min_event.unset()

        if self.is_max():
            self._max_event.set()

    def decr(self) -> None:
        if self.is_min():
            raise LowThresholdError()

        self._value -= 1
        self._max_event.unset()

        if self.is_min():
            self._min_event.set()

    def reset(self) -> None:
        self._set_value(0)

    def is_min(self) -> bool:
        return self._value <= self._min

    def is_max(self) -> bool:
        return self._value >= self._max

    def value(self) -> int:
        return self._value
