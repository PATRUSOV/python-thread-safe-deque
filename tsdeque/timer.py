import time
from typing import Optional, Union


class Timer:
    def __init__(self, period: float) -> None:
        self._period = period
        self._start = time.perf_counter()

    def get_spend(self) -> float:
        elapsed = time.perf_counter() - self._start
        remainder = max(0, self._period - elapsed)
        return remainder


class NullTimer:
    def get_spend(self) -> None:
        return None


def get_timer(period: Optional[float]) -> Union[Timer, NullTimer]:
    if period is None:
        return NullTimer()
    else:
        return Timer(period)
