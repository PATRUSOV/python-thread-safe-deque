import pytest
import time

from threading import Thread

from tsdeque.devent import Devent


@pytest.fixture
def devent() -> Devent:
    return Devent()


def test_start_state_of_devent(devent: Devent):
    assert not devent.is_set()


def test_waiting_unset_state(devent: Devent):
    devent.set()

    def event_unset_waiter() -> None:
        devent.wait_unset()

    thread_waiter = Thread(target=event_unset_waiter)
    thread_waiter.start()

    time.sleep(0.02)
    devent.unset()

    thread_waiter.join(timeout=0.2)
    assert not thread_waiter.is_alive(), "unset_wait got stuck."


def test_waiting_set_state(devent: Devent):
    devent.unset()

    def event_set_waiter() -> None:
        devent.wait_set()

    thread_waiter = Thread(target=event_set_waiter)
    thread_waiter.start()

    time.sleep(0.02)
    devent.set()

    thread_waiter.join(timeout=0.2)
    assert not thread_waiter.is_alive(), "set_wait got stuck."


def test_unset_waiting_timeout(devent: Devent):
    devent.set()
    timeout = 0.2

    start_time = time.monotonic()
    result = devent.wait_unset(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert result is False, f"wait_unset returned not False, but {result}"

    assert elapsed_time == pytest.approx(timeout, rel=0.1), (
        f"Measured time: {elapsed_time} did not match expected: {timeout}"
    )


def test_set_waiting_timeout(devent: Devent):
    devent.unset()
    timeout = 0.2

    start_time = time.monotonic()
    result = devent.wait_set(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert result is False, f"wait_set returned not False, but {result}"

    assert elapsed_time == pytest.approx(timeout, rel=0.1), (
        f"Measured time: {elapsed_time} did not match expected: {timeout}"
    )
