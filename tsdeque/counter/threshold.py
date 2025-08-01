from typing import TYPE_CHECKING
from dataclasses import dataclass


if TYPE_CHECKING:
    from tsdeque.devent import Devent
    from tsdeque.counter.nulldevent import _NullDevent


@dataclass
class Threshold:
    value: int
    event: Devent | _NullDevent
