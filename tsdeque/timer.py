import time
from typing import Optional, Union


class Timer:
    """Timer that measures elapsed time against a specified period."""

    def __init__(self, period: float) -> None:
        """Initializes the timer with a given period.

        Args:
            period (float): The total time period for the timer in seconds.
        """
        self._period = period
        self._start = time.perf_counter()

    def get_spend(self) -> float:
        """Calculates the remaining time before the period elapses.

        Returns:
            float: Remaining time in seconds; never negative (minimum zero).
        """
        elapsed = time.perf_counter() - self._start
        remainder = max(0, self._period - elapsed)
        return remainder


class NullTimer:
    """Timer stub that represents an infinite or no timeout."""

    def get_spend(self) -> None:
        """Returns None to indicate no timeout.

        Returns:
            None
        """
        return None


def get_timer(period: Optional[float]) -> Union[Timer, NullTimer]:
    """Factory function returning a Timer or NullTimer based on the period.

    Args:
        period (Optional[float]): Desired timeout period in seconds, or None for no timeout.

    Returns:
        Timer or NullTimer: Timer instance corresponding to the given period.
    """
    if period is None:
        return NullTimer()
    else:
        return Timer(period)
