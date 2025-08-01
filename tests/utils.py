import pytest
import time


def accurate_sleep(period: float) -> None:
    """Sleep for the specified period and assert the actual sleep duration matches the requested time."""
    start_time = time.monotonic()
    time.sleep(period)
    measured_time = time.monotonic() - start_time

    assert measured_time == pytest.approx(period, rel=0.1), (
        f"Measured sleep time: {measured_time} did not match expected: {period}."
    )
