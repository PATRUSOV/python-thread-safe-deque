import math

from tsdeque.counter.threshold import Threshold
from tsdeque.counter.exceptions import LowThresholdError, HighThresholdError

LOW_UNLIMITED_THRESHOLD = Threshold(value=-math.inf)
HIGH_UNLIMITED_THRESHOLD = Threshold(value=math.inf)


class Counter:
    """Counter with configurable lower and upper thresholds that trigger events.

    Attributes:
        _min_event: Event triggered when the counter reaches the lower threshold.
        _max_event: Event triggered when the counter reaches the upper threshold.
        _min: Integer representing the lower threshold value.
        _max: Integer representing the upper threshold value.
        _value: Current value of the counter.
    """

    def __init__(
        self,
        value: int = 0,
        low_threshold: Threshold = LOW_UNLIMITED_THRESHOLD,
        high_threshold: Threshold = HIGH_UNLIMITED_THRESHOLD,
    ) -> None:
        """Initializes the Counter with initial value and threshold limits.

        Args:
            value (int): Initial counter value.
            low_threshold (Threshold): Lower threshold with associated event.
            high_threshold (Threshold): Upper threshold with associated event.

        Raises:
            ValueError: If high_threshold.value is not greater than low_threshold.value.
        """
        self._min_event = low_threshold.event
        self._max_event = high_threshold.event

        self._min = low_threshold.value
        self._max = high_threshold.value

        if not self._max > self._min:
            raise ValueError("Upper threshold must be greater than lower threshold.")

        self._set_value(value)

    def _set_value(self, value: int):
        """Sets the internal counter value with threshold checks and event updates.

        Args:
            value (int): New value to set.

        Raises:
            LowThresholdError: If value is less than the lower threshold.
            HighThresholdError: If value is greater than the upper threshold.
        """
        if value < self._min:
            raise LowThresholdError()
        elif value > self._max:
            raise HighThresholdError()

        self._value = value

        if self._value == self._min:
            self._min_event.set()
            self._max_event.unset()
        elif self._value == self._max:
            self._max_event.set()
            self._min_event.unset()
        else:
            self._max_event.unset()
            self._min_event.unset()

    def set_value(self, value: int) -> None:
        """Public method to update the counter's value.

        Args:
            value (int): Value to set.
        """
        self._set_value(value)

    def incr(self) -> None:
        """Increments the counter by one and updates events accordingly.

        Raises:
            HighThresholdError: If incrementing exceeds the upper threshold.
        """
        if self.is_max():
            raise HighThresholdError()

        self._value += 1
        self._min_event.unset()

        if self.is_max():
            self._max_event.set()

    def decr(self) -> None:
        """Decrements the counter by one and updates events accordingly.

        Raises:
            LowThresholdError: If decrementing goes below the lower threshold.
        """
        if self.is_min():
            raise LowThresholdError()

        self._value -= 1
        self._max_event.unset()

        if self.is_min():
            self._min_event.set()

    def reset(self) -> None:
        """Resets the counter value to zero and updates events."""
        self._set_value(0)

    def is_min(self) -> bool:
        """Checks if the current value is at or below the lower threshold.

        Returns:
            bool: True if value <= lower threshold, else False.
        """
        return self._value <= self._min

    def is_max(self) -> bool:
        """Checks if the current value is at or above the upper threshold.

        Returns:
            bool: True if value >= upper threshold, else False.
        """
        return self._value >= self._max

    def value(self) -> int:
        """Returns the current value of the counter.

        Returns:
            int: Current counter value.
        """
        return self._value
