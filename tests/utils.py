import pytest
import time


def accurate_sleep(period: float) -> None:
    """time.sleep() с проверкой что сон был именно столько, сколько было указанно."""
    start_time = time.monotonic()
    time.sleep(period)
    measured_time = time.monotonic() - start_time

    assert measured_time == pytest.approx(period, rel=0.1), (
        f"Замереное время сна: {measured_time}, не совпало с ожидаемым: {period}."
    )
