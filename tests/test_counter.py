import pytest

from tsdeque.counter import Counter, Threshold, LowThresholdError, HighThresholdError
from tsdeque.devent import Devent


@pytest.fixture
def standart_counter() -> Counter:
    return Counter()


def test_low_threshold_exception():
    counter = Counter(low_threshold=Threshold(-3))

    for _ in range(3):
        counter.decr()

    with pytest.raises(LowThresholdError):
        counter.decr()


def test_high_threshold_exception():
    counter = Counter(high_threshold=Threshold(3))

    for _ in range(3):
        counter.incr()

    with pytest.raises(HighThresholdError):
        counter.incr()


def test_low_threshold_event():
    low_event = Devent()

    counter = Counter(low_threshold=Threshold(-3, low_event))
    assert not low_event.is_set()

    for _ in range(2):
        counter.decr()
        assert not low_event.is_set()

    counter.decr()
    assert low_event.is_set()


def test_high_threshold_event():
    high_event = Devent()

    counter = Counter(high_threshold=Threshold(3, high_event))
    assert not high_event.is_set()

    for _ in range(2):
        counter.incr()
        assert not high_event.is_set()

    counter.incr()
    assert high_event.is_set()


def test_zero_range_span():
    with pytest.raises(ValueError):
        Counter(low_threshold=Threshold(1), high_threshold=Threshold(1))


def test_getting_value(standart_counter: Counter):
    standart_counter.incr()
    assert standart_counter.value() == 1


def test_reset_counter(standart_counter: Counter):
    standart_counter.incr()
    assert standart_counter.value() == 1
    standart_counter.reset()
    assert standart_counter.value() == 0


def test_reset_low_event():
    low_event = Devent()
    counter = Counter(low_threshold=Threshold(-3, low_event))

    for _ in range(3):
        counter.decr()

    assert low_event.is_set()
    counter.reset()
    assert not low_event.is_set()


def test_reset_high_event():
    high_event = Devent()
    counter = Counter(high_threshold=Threshold(3, high_event))

    for _ in range(3):
        counter.incr()

    assert high_event.is_set()
    counter.reset()
    assert not high_event.is_set()


def test_start_state(standart_counter: Counter):
    assert standart_counter.value() == 0


def test_low_threshold_triggered_on_initial_value():
    low_event = Devent()
    Counter(low_threshold=Threshold(0, low_event))
    assert low_event.is_set()


def test_high_threshold_triggered_on_initial_value():
    high_event = Devent()
    Counter(high_threshold=Threshold(0, high_event))
    assert high_event.is_set()


def test_is_min():
    counter = Counter(low_threshold=Threshold(-3))
    assert not counter.is_min()

    for _ in range(2):
        counter.decr()
        assert not counter.is_min()

    counter.decr()
    assert counter.is_min()


def test_is_max():
    counter = Counter(high_threshold=Threshold(3))
    assert not counter.is_max()

    for _ in range(2):
        counter.incr()
        assert not counter.is_max()

    counter.incr()
    assert counter.is_max()


def test_set_value():
    counter = Counter()
    counter.set_value(3)
    assert counter.value() == 3


def test_set_value_exceeding_the_min_threshold():
    counter = Counter(low_threshold=Threshold(-3))
    with pytest.raises(LowThresholdError):
        counter.set_value(-4)


def test_set_value_exceeding_the_max_threshold():
    counter = Counter(high_threshold=Threshold(3))
    with pytest.raises(HighThresholdError):
        counter.set_value(4)


def test_set_value_triggers_low_threshold_event():
    low_event = Devent()
    counter = Counter(low_threshold=Threshold(-3, low_event))
    assert not low_event.is_set()

    counter.set_value(-3)
    assert low_event.is_set()


def test_set_value_triggers_high_threshold_event():
    high_event = Devent()
    counter = Counter(high_threshold=Threshold(3, high_event))
    assert not high_event.is_set()

    counter.set_value(3)
    assert high_event.is_set()
