from collections import deque
from threading import Lock, Event
from typing import Generic, TypeVar, Deque, TypeAlias, Optional
from time import perf_counter


class Timer:
    def __init__(self, period: float) -> None:
        self._period = period
        self._start = perf_counter()

    def get_spend(self) -> float:
        elapsed = perf_counter() - self._start
        remainder = max(0, self._period - elapsed)
        return remainder


class Devent:
    def __init__(self):
        self._set_event = Event()
        self._unset_event = Event()
        self._mutex = Lock()
        self.unset()

    def is_set(self):
        return self._set_event.is_set()

    def set(self) -> None:
        with self._mutex:
            self._set_event.set()
            self._unset_event.clear()

    def unset(self) -> None:
        with self._mutex:
            self._set_event.clear()
            self._unset_event.set()

    def wait_set(self, timeout: Optional[float] = None) -> bool:
        with self._mutex:
            return self._set_event.wait(timeout)

    def wait_unset(self, timeout: Optional[float] = None) -> bool:
        with self._mutex:
            return self._unset_event.wait(timeout)


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

    def append(self, item: T, timeout: Optional[float]) -> None:
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

    def lappend(self, item: T, timeout: Optional[float]) -> None:
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

    def pop(self, timeout: Optional[float]) -> T:
        timer = Timer(timeout) if timeout is not None else None

        while True:
            wait_time = timer.get_spend() if timer is not None else None

            if not self._empty_event.wait_unset(wait_time):
                raise TimeoutError("Установленный временной лимит вышел.")

            with self._mutex:
                if len(self._deque) > 0:
                    item = self._deque.pop()
                    return item

    def lpop(self, timeout: Optional[float]) -> T:
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


TSDeque: TypeAlias = ThreadSafeDeque

__all__ = ["TSDeque", "ThreadSafeDeque"]
