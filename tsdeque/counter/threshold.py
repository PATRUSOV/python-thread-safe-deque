from typing import Union
from dataclasses import dataclass

from tsdeque.counter.nulldevent import _NULL_DEVENT, _NullDevent
from tsdeque.devent import Devent


@dataclass
class Threshold:
    """
    Represents a threshold value paired with an associated event.

    Attributes:
        value (int): The threshold numeric value.
        event (Union[Devent, _NullDevent]): Event triggered when threshold is reached or cleared.
            Defaults to a no-op event.
    """

    value: int
    event: Union[Devent, _NullDevent] = _NULL_DEVENT
