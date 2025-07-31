import time
import pytest
import logging
from threading import Thread

from tsdeque.core import ThreadSafeDeque

logger = logging.getLogger()


def unlimited_deque() -> ThreadSafeDeque:
    return ThreadSafeDeque()


@pytest.fixture
def three_elemet_deque() -> ThreadSafeDeque:
    return ThreadSafeDeque(3)


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


def test_producent_and_consument(three_elemet_deque: ThreadSafeDeque):
    objects = [object(), object(), object()]

    def producent():
        for obj in objects:
            three_elemet_deque.put(obj)

    def consument():
        for obj in objects:
            output = three_elemet_deque.getleft()
            assert obj is output

    producent_thread = Thread(target=producent)
    consument_thread = Thread(target=consument)

    producent_thread.start()
    consument_thread.start()

    producent_thread.join()
    consument_thread.join()

    assert not producent_thread.is_alive()
    assert not consument_thread.is_alive()


def test_start_state(three_elemet_deque: ThreadSafeDeque):
    assert three_elemet_deque.active_tasks() == 0
    assert len(three_elemet_deque) == 0

    # проверка что join срабатывает сразу
    start_time = time.monotonic()
    three_elemet_deque.join()
    elapsed_time = time.monotonic() - start_time

    assert elapsed_time <= 0.1


def test_task_counting(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())
    three_elemet_deque.get()

    assert three_elemet_deque.active_tasks() == 1
    assert len(three_elemet_deque) == 0

    three_elemet_deque.task_done()
    assert three_elemet_deque.active_tasks() == 0


def test_join_timeout(three_elemet_deque: ThreadSafeDeque):
    three_elemet_deque.put(object())

    timeout = 0.2

    start_time = time.monotonic()
    three_elemet_deque.join(timeout=timeout)
    elapsed_time = time.monotonic() - start_time

    assert timeout == pytest.approx(elapsed_time, rel=0.1)
