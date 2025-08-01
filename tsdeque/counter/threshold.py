from typing import Union, TYPE_CHECKING
from dataclasses import dataclass

from tsdeque.counter.nulldevent import _NULL_DEVENT

if TYPE_CHECKING:
    from tsdeque.devent import Devent
    from tsdeque.counter.nulldevent import _NullDevent


@dataclass
class Threshold:
    value: int
    event: Union[Devent, _NullDevent] = _NULL_DEVENT
