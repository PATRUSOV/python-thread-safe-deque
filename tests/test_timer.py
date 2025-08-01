import pytest

from tsdeque.timer import Timer, NullTimer, get_timer
from tests.utils import accurate_sleep


@pytest.fixture
def half_second_timer() -> Timer:
    return Timer(0.5)


def test_measuring_time_before_timeout(half_second_timer: Timer):
    period = 0.2

    accurate_sleep(period)

    time_left_measured = half_second_timer.get_spend()
    time_left_calculated = 0.5 - period

    assert time_left_calculated == pytest.approx(time_left_measured, rel=0.1), (
        f"Expected remaining time: {time_left_calculated}, but got: {time_left_measured}"
    )


def test_measuring_time_after_timeout(half_second_timer: Timer):
    accurate_sleep(0.6)

    assert half_second_timer.get_spend() == 0


def test_measuring_negative_time():
    negative_timer = Timer(-1)

    assert negative_timer.get_spend() == 0


def test_getting_timer():
    null_timer = get_timer(None)
    standart_timer = get_timer(2)

    assert isinstance(null_timer, NullTimer), (
        f"Expected {NullTimer.__name__}(), but got {null_timer}"
    )
    assert isinstance(standart_timer, Timer), (
        f"Expected {Timer.__name__}(), but got {standart_timer}"
    )
