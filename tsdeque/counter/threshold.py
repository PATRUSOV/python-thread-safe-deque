from typing import Union
from dataclasses import dataclass

from tsdeque.counter.nulldevent import _NULL_DEVENT, _NullDevent
from tsdeque.devent import Devent


@dataclass
class Threshold:
    value: int
    event: Union[Devent, _NullDevent] = _NULL_DEVENT
