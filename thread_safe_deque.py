from collections import deque
from threading import Lock, Event
from typing import Generic, TypeVar, Deque, TypeAlias

T = TypeVar("T")

# TODO: Добавить:
# +Таймеры
# +Документацию


class ThreadSafeDeque(Generic[T]):
    def __init__(self):
        self._deque: Deque[T] = deque()
        self._mutex = Lock()
        self._join_event = Event()
        self._not_null_event = Event()
        self._not_null_event.clear()
        self._tasks_counter = 0

    def append(self, item: T) -> None:
        with self._mutex:
            self._deque.append(item)
            self._tasks_counter += 1
            self._not_null_event.set()
            self._join_event.clear()

    def lappend(self, item: T) -> None:
        with self._mutex:
            self._deque.appendleft(item)
            self._tasks_counter += 1
            self._not_null_event.set()
            self._join_event.clear()

    def pop(self) -> T:
        while True:
            self._not_null_event.wait()
            with self._mutex:
                if len(self._deque) > 0:
                    item = self._deque.pop()
                    return item

    def lpop(self) -> T:
        while True:
            self._not_null_event.wait()
            with self._mutex:
                if len(self._deque) > 0:
                    item = self._deque.popleft()
                    return item

    def clear(self) -> None:
        with self._mutex:
            self._deque.clear()
            self._not_null_event.clear()
            self._tasks_counter = 0
            self._join_event.set()

    def join(self) -> None:
        self._join_event.wait()

    def task_done(self) -> None:
        with self._mutex:
            if self._tasks_counter == 0:
                raise ValueError("Все задачи уже выполнены.")
            self._tasks_counter -= 1
            if self._tasks_counter == 0:
                self._join_event.set()
                self._not_null_event.clear()

    def __len__(self) -> int:
        with self._mutex:
            return len(self._deque)


TSDeque: TypeAlias = ThreadSafeDeque

__all__ = ["TSDeque", "ThreadSafeDeque"]
