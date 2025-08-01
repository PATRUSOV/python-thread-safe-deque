from collections import deque
from threading import Lock
from typing import Generic, TypeVar, Deque, Optional

import tsdeque.timer as tmr
from tsdeque.devent import Devent
from tsdeque.counter import Counter, Threshold, LowThresholdError
from tsdeque.exceptions import NoActiveTaskError

T = TypeVar("T")


class ThreadSafeDeque(Generic[T]):
    """
    Потокобезопасная, двухсторонняя очредь.
    """

    def __init__(self, maxsize: int = 0):
        self._deque: Deque[T] = deque()

        self._mutex = Lock()
        self._empty_event = Devent()

        if maxsize < 0:
            raise ValueError("Размер очереди не может быть отрицательным.")
        self._limitation = maxsize > 0

        if self._limitation:
            self._full_event = Devent()
            self._item_counter = Counter(
                value=0,
                high_threshold=Threshold(value=maxsize, event=self._full_event),
            )

        self._tasks_counter = Counter(
            value=0,
            low_threshold=Threshold(value=0, event=self._empty_event),
        )

    def _base_put(self, item: T, timeout: Optional[float], left: bool) -> None:
        timer = tmr.get_timer(timeout)

        while True:
            wait_time = timer.get_spend()
            if self._limitation:
                if not self._full_event.wait_unset(wait_time):
                    raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if not self._full_event.is_set():
                    if left:
                        self._deque.appendleft(item)
                    else:
                        self._deque.append(item)

                    self._tasks_counter.incr()
                    if self._limitation:
                        self._item_counter.incr()
                    break

    def _base_get(self, timeout: Optional[float], left: bool) -> T:
        timer = tmr.get_timer(timeout)

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

                    if self._limitation:
                        self._item_counter.decr()
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
            self._tasks_counter.set_value(
                self._tasks_counter.value() - len(self._deque)
            )
            self._deque.clear()
            if self._limitation:
                self._item_counter.reset()

    def join(self, timeout: Optional[float] = None) -> None:
        self._empty_event.wait_set(timeout)

    def task_done(self) -> None:
        with self._mutex:
            try:
                self._tasks_counter.decr()
            except LowThresholdError:
                raise NoActiveTaskError("Все задачи уже выполнены.")

    def tasks_count(self) -> int:
        with self._mutex:
            return self._tasks_counter.value()

    def __len__(self) -> int:
        with self._mutex:
            return len(self._deque)
