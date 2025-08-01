import time
import pytest
from threading import Thread

from tsdeque.core import ThreadSafeDeque
from tsdeque.exceptions import NoActiveTaskError


@pytest.fixture
def three_elemet_deque() -> ThreadSafeDeque:
    return ThreadSafeDeque(3)


@pytest.fixture
def unlimited_deque() -> ThreadSafeDeque:
    return ThreadSafeDeque()


def test_put_and_get(three_elemet_deque: ThreadSafeDeque):
    item = object()

    three_elemet_deque.put(item)
    output = three_elemet_deque.get()

    assert output is item


def test_get_timeout(three_elemet_deque: ThreadSafeDeque):
    timeout = 0.2

    start_time = time.monotonic()
    with pytest.raises(TimeoutError):
        three_elemet_deque.get(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert elapsed_time == pytest.approx(timeout, rel=0.1)


def test_put_timeout(three_elemet_deque: ThreadSafeDeque):
    for _ in range(3):
        three_elemet_deque.put(object())

    timeout = 0.2

    start_time = time.monotonic()
    with pytest.raises(TimeoutError):
        three_elemet_deque.put(object(), timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert elapsed_time == pytest.approx(timeout, rel=0.1)


def test_get_and_put_with_unlimited_deque(unlimited_deque: ThreadSafeDeque):
    obj = object()

    unlimited_deque.put(obj)
    result = unlimited_deque.get()

    assert result is obj


def test_producent_and_consument(three_elemet_deque: ThreadSafeDeque):
    objects = [object(), object(), object()]

    def producent():
        for obj in objects:
            three_elemet_deque.put(obj)

    def consument():
        for obj in objects:
            output = three_elemet_deque.getleft()
            assert obj is output
            three_elemet_deque.task_done()

    producent_thread = Thread(target=producent)
    consument_thread = Thread(target=consument)

    producent_thread.start()
    consument_thread.start()

    three_elemet_deque.join()

    producent_thread.join()
    consument_thread.join()

    assert not producent_thread.is_alive()
    assert not consument_thread.is_alive()


def test_start_state(three_elemet_deque: ThreadSafeDeque):
    assert three_elemet_deque.tasks_count() == 0
    assert len(three_elemet_deque) == 0

    # check that join returns immediately
    start_time = time.monotonic()
    three_elemet_deque.join()
    elapsed_time = time.monotonic() - start_time

    assert elapsed_time <= 0.1


def test_task_counting(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())
    three_elemet_deque.get()

    assert three_elemet_deque.tasks_count() == 1
    assert len(three_elemet_deque) == 0

    three_elemet_deque.task_done()
    assert three_elemet_deque.tasks_count() == 0


def test_join_timeout(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())

    timeout = 0.2

    start_time = time.monotonic()
    three_elemet_deque.join(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert timeout == pytest.approx(elapsed_time, rel=0.1)


def test_join_with_unfinished_task(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())
    three_elemet_deque.get()

    timeout = 0.2

    # until task_done() is called, join() will remain blocked and wait for timeout
    start_time = time.monotonic()
    three_elemet_deque.join(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert timeout == pytest.approx(elapsed_time, rel=0.1)

    three_elemet_deque.task_done()

    timeout = 1

    # after calling task_done, join should unblock immediately (definitely faster than timeout)
    start_time = time.monotonic()
    three_elemet_deque.join(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert elapsed_time < 0.1


def test_clear(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())

    assert three_elemet_deque.tasks_count() == 1
    assert len(three_elemet_deque) == 1

    three_elemet_deque.clear()

    assert three_elemet_deque.tasks_count() == 0
    assert len(three_elemet_deque) == 0


def test_clear_with_unfinished_task(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())
    three_elemet_deque.get()

    assert three_elemet_deque.tasks_count() == 1

    three_elemet_deque.clear()

    assert three_elemet_deque.tasks_count() == 1


def test_task_done_with_empty_deque(three_elemet_deque: ThreadSafeDeque):
    assert three_elemet_deque.tasks_count() == 0

    with pytest.raises(NoActiveTaskError):
        three_elemet_deque.task_done()
