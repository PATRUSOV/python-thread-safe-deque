from collections import deque
from threading import Lock
from typing import Generic, TypeVar, Deque, Optional

import tsdeque.timer as t
from tsdeque.devent import Devent
from tsdeque.counter import Counter

T = TypeVar("T")


class ThreadSafeDeque(Generic[T]):
    """
    Потокобезопасная, двухсторонняя очредь.
    """

    def __init__(self, maxsize: int = 0):
        self._deque: Deque[T] = deque()
        self._tasks_counter = Counter()

        self._mutex = Lock()
        self._empty_event = Devent()
        self._full_event = Devent()

        if maxsize < 0:
            raise ValueError("Размер очереди не может быть отрицательным.")

        self._empty_event.set()

        self._max_tasks = maxsize
        self._limitation = self._max_tasks > 0

    def _base_put(self, item: T, timeout: Optional[float], left: bool) -> None:
        timer = t.get_timer(timeout)

        while True:
            wait_time = timer.get_spend()
            if not self._full_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if not self._full_event.is_set():
                    if left:
                        self._deque.appendleft(item)
                    else:
                        self._deque.append(item)
                    self._tasks_counter.incr()
                    self._empty_event.unset()

                    if (
                        self._limitation
                        and self._tasks_counter.value() >= self._max_tasks
                    ):
                        self._full_event.set()
                    break

    def _base_get(self, timeout: Optional[float], left: bool) -> T:
        timer = t.get_timer(timeout)

        while True:
            wait_time = timer.get_spend()

            if not self._empty_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if len(self._deque) > 0:
                    if left:
                        item = self._deque.popleft()
                    else:
                        item = self._deque.pop()

                    if (
                        self._limitation
                        and self._tasks_counter.value() >= self._max_tasks
                    ):
                        self._full_event.set()

                    if len(self._deque) == 0:
                        self._empty_event.set()

                    return item

    def put(self, item: T, timeout: Optional[float] = None) -> None:
        self._base_put(
            item=item,
            timeout=timeout,
            left=False,
        )

    def putleft(self, item: T, timeout: Optional[float] = None) -> None:
        self._base_put(
            item=item,
            timeout=timeout,
            left=True,
        )

    def get(self, timeout: Optional[float] = None) -> T:
        return self._base_get(
            timeout=timeout,
            left=False,
        )

    def getleft(self, timeout: Optional[float] = None) -> T:
        return self._base_get(
            timeout=timeout,
            left=True,
        )

    def clear(self) -> None:
        with self._mutex:
            self._deque.clear()
            self._tasks_counter.reset()
            self._full_event.unset()
            self._empty_event.set()

    def join(self, timeout: Optional[float] = None) -> None:
        self._empty_event.wait_set(timeout)

    def task_done(self) -> None:
        with self._mutex:
            if self._tasks_counter.is_zero():
                raise ValueError("Все задачи уже выполнены.")

            self._tasks_counter.decr()
            if self._tasks_counter.is_zero():
                self._empty_event.set()

    def active_tasks(self) -> int:
        with self._mutex:
            return self._tasks_counter.value()

    def __len__(self) -> int:
        with self._mutex:
            return len(self._deque)
