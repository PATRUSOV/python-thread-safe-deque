from collections import deque
from threading import Lock
from typing import Generic, TypeVar, Deque, Optional

from tsdeque.devent import Devent
from tsdeque.timer import Timer

T = TypeVar("T")

# TODO: Добавить:
# +Документацию
# +Тесты
# FIXME: Исправить:
# +Убрать дублирование кода


class ThreadSafeDeque(Generic[T]):
    """
    Потокобезопасная, двухсторонняя очредь.
    """

    def __init__(self, maxsize: int = 0):
        self._deque: Deque[T] = deque()
        self._mutex = Lock()
        self._empty_event = Devent()
        self._tasks_counter = 0
        self._full_event = Devent()

        if maxsize < 0:
            raise ValueError("Размер очереди не может быть отрицательным.")

        self._max_tasks = maxsize
        self._limitation = self._max_tasks > 0

        self._empty_event.set()

    def put(self, item: T, timeout: Optional[float] = None) -> None:
        timer = Timer(timeout) if timeout is not None else None

        while True:
            wait_time = timer.get_spend() if timer is not None else None
            if not self._full_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if not self._full_event.is_set():
                    self._deque.append(item)
                    self._tasks_counter += 1
                    self._empty_event.unset()

                    if self._limitation and self._tasks_counter >= self._max_tasks:
                        self._full_event.set()

    def lput(self, item: T, timeout: Optional[float] = None) -> None:
        timer = Timer(timeout) if timeout is not None else None

        while True:
            wait_time = timer.get_spend() if timer is not None else None

            if not self._full_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if not self._full_event.is_set():
                    self._deque.appendleft(item)
                    self._tasks_counter += 1
                    self._empty_event.unset()

                    if self._limitation and self._tasks_counter >= self._max_tasks:
                        self._full_event.set()

    def get(self, timeout: Optional[float] = None) -> T:
        timer = Timer(timeout) if timeout is not None else None

        while True:
            wait_time = timer.get_spend() if timer is not None else None

            if not self._empty_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if len(self._deque) > 0:
                    item = self._deque.pop()
                    return item

    def lget(self, timeout: Optional[float] = None) -> T:
        timer = Timer(timeout) if timeout is not None else None

        while True:
            wait_time = timer.get_spend() if timer is not None else None

            if not self._empty_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if len(self._deque) > 0:
                    item = self._deque.popleft()
                    return item

    def clear(self) -> None:
        with self._mutex:
            self._deque.clear()
            self._tasks_counter = 0
            self._full_event.unset()
            self._empty_event.set()

    def join(self, timeout: Optional[float] = None) -> None:
        self._empty_event.wait_set(timeout)

    def task_done(self) -> None:
        with self._mutex:
            if self._tasks_counter == 0:
                raise ValueError("Все задачи уже выполнены.")
            self._tasks_counter -= 1
            if self._tasks_counter == 0:
                self._empty_event.set()

    def __len__(self) -> int:
        with self._mutex:
            return len(self._deque)
