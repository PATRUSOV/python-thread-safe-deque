import time


class Timer:
    def __init__(self, period: float) -> None:
        self._period = period
        self._start = time.perf_counter()

    def get_spend(self) -> float:
        elapsed = time.perf_counter() - self._start
        remainder = max(0, self._period - elapsed)
        return remainder
