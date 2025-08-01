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
    A thread-safe double-ended queue with optional capacity limit and task tracking.

    Supports blocking and timeout-aware operations for adding and retrieving items
    from either end. Maintains internal counters for active items and tasks,
    allowing join-style synchronization for task completion.
    """

    def __init__(self, maxsize: int = 0):
        """
        Initializes the deque.

        Args:
            maxsize (int): Maximum number of items allowed in the queue. If 0 or less,
                the queue is unbounded.

        Raises:
            ValueError: If maxsize is negative.
        """
        self._deque: Deque[T] = deque()

        self._mutex = Lock()
        self._empty_event = Devent()

        if maxsize < 0:
            raise ValueError("Queue size cannot be negative.")
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
        """
        Internal method to insert an item into the queue from either end,
        respecting optional timeout and capacity limits.

        Args:
            item (T): The item to insert.
            timeout (Optional[float]): Maximum time to wait if the queue is full.
                If None, the method blocks indefinitely.
            left (bool): If True, inserts the item at the left end; otherwise, at the right.

        Raises:
            TimeoutError: If the timeout is reached while waiting for space to become available.
        """
        if self._limitation:
            timer = tmr.get_timer(timeout)

        while True:
            if self._limitation:
                wait_time = timer.get_spend()  # type: ignore
                if not self._full_event.wait_unset(wait_time):
                    raise TimeoutError(
                        "The timeout has expired while waiting for available space."
                    )

            with self._mutex:
                if self._limitation:
                    if self._full_event.is_set():
                        continue

                if left:
                    self._deque.appendleft(item)
                else:
                    self._deque.append(item)

                self._tasks_counter.incr()
                if self._limitation:
                    self._item_counter.incr()
                break

    def _base_get(self, timeout: Optional[float], left: bool) -> T:
        """
        Internal method to remove and return an item from the queue from either end,
        respecting optional timeout and availability constraints.

        Args:
            timeout (Optional[float]): Maximum time to wait if the queue is empty.
                If None, the method blocks indefinitely.
            left (bool): If True, removes the item from the left end; otherwise, from the right.

        Returns:
            T: The item retrieved from the queue.

        Raises:
            TimeoutError: If the timeout is reached while waiting for an item to become available.
        """
        timer = tmr.get_timer(timeout)

        while True:
            wait_time = timer.get_spend()

            if not self._empty_event.wait_unset(wait_time):
                raise TimeoutError("The timeout has expired while waiting for an item.")

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
        """
        Inserts an item at the right end of the queue.

        Args:
            item (T): The item to insert.
            timeout (Optional[float]): Maximum time to wait for free space.
                If None, waits indefinitely.

        Raises:
            TimeoutError: If the operation times out.
        """
        self._base_put(
            item=item,
            timeout=timeout,
            left=False,
        )

    def putleft(self, item: T, timeout: Optional[float] = None) -> None:
        """
        Inserts an item at the left end of the queue.

        Args:
            item (T): The item to insert.
            timeout (Optional[float]): Maximum time to wait for free space.
                If None, waits indefinitely.

        Raises:
            TimeoutError: If the operation times out.
        """
        self._base_put(
            item=item,
            timeout=timeout,
            left=True,
        )

    def get(self, timeout: Optional[float] = None) -> T:
        """
        Removes and returns an item from the right end of the queue.

        Args:
            timeout (Optional[float]): Maximum time to wait for an item.
                If None, waits indefinitely.

        Returns:
            T: The retrieved item.

        Raises:
            TimeoutError: If the operation times out.
        """
        return self._base_get(
            timeout=timeout,
            left=False,
        )

    def getleft(self, timeout: Optional[float] = None) -> T:
        """
        Removes and returns an item from the left end of the queue.

        Args:
            timeout (Optional[float]): Maximum time to wait for an item.
                If None, waits indefinitely.

        Returns:
            T: The retrieved item.

        Raises:
            TimeoutError: If the operation times out.
        """
        return self._base_get(
            timeout=timeout,
            left=True,
        )

    def clear(self) -> None:
        """
        Removes all items from the queue and resets internal counters.
        """
        with self._mutex:
            self._tasks_counter.set_value(
                self._tasks_counter.value() - len(self._deque)
            )
            self._deque.clear()
            if self._limitation:
                self._item_counter.reset()

    def join(self, timeout: Optional[float] = None) -> None:
        """
        Blocks until all items in the queue have been marked as done via `task_done`.

        Args:
            timeout (Optional[float]): Maximum time to wait. If None, waits indefinitely.

        Raises:
            TimeoutError: If the operation times out.
        """
        self._empty_event.wait_set(timeout)

    def task_done(self) -> None:
        """
        Decrements the internal task counter. Used to indicate that a previously
        enqueued task is complete.

        Raises:
            NoActiveTaskError: If called more times than there were tasks.
        """
        with self._mutex:
            try:
                self._tasks_counter.decr()
            except LowThresholdError:
                raise NoActiveTaskError("All tasks have already been completed.")

    def tasks_count(self) -> int:
        """
        Returns the current number of active tasks.

        Returns:
            int: The number of unfinished tasks.
        """
        with self._mutex:
            return self._tasks_counter.value()

    def __len__(self) -> int:
        """
        Returns the number of items currently stored in the queue.

        Returns:
            int: The number of items in the queue.
        """
        with self._mutex:
            return len(self._deque)
