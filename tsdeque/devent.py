from threading import Lock, Event
from typing import Optional


class Devent:
    def __init__(self):
        self._set_event = Event()
        self._unset_event = Event()
        self._mutex = Lock()
        self.unset()

    def is_set(self) -> bool:
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
