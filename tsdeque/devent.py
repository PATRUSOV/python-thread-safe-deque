from threading import Lock, Event
from typing import Optional


class Devent:
    """
    Dual-state event object for signaling both set and unset states.
    Thread-safe.
    """

    def __init__(self):
        """Initializes the Devent object with default unset state."""
        self._set_event = Event()
        self._unset_event = Event()
        self._mutex = Lock()
        self.unset()

    def is_set(self) -> bool:
        """Returns whether the event is currently set.

        Returns:
            bool: True if the event is set, False otherwise.
        """
        with self._mutex:
            return self._set_event.is_set()

    def set(self) -> None:
        """Sets the event.

        Signals the 'set' state and clears the 'unset' state.
        """
        with self._mutex:
            self._set_event.set()
            self._unset_event.clear()

    def unset(self) -> None:
        """Unsets the event.

        Signals the 'unset' state and clears the 'set' state.
        """
        with self._mutex:
            self._set_event.clear()
            self._unset_event.set()

    def wait_set(self, timeout: Optional[float] = None) -> bool:
        """Blocks until the event is set or until the timeout elapses.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. If None, blocks indefinitely.

        Returns:
            bool: True if the event is set, False if the timeout elapsed.
        """
        return self._set_event.wait(timeout)

    def wait_unset(self, timeout: Optional[float] = None) -> bool:
        """Blocks until the event is unset or until the timeout elapses.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. If None, blocks indefinitely.

        Returns:
            bool: True if the event is unset, False if the timeout elapsed.
        """
        return self._unset_event.wait(timeout)
