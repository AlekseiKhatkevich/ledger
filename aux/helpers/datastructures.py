from collections import OrderedDict
from typing import Hashable, Generic, TypeVar

_T = TypeVar("_T", bound=Hashable)


class FixedSizeSet(Generic[_T]):
    def __init__(self, capacity: int = 100) -> None:
        self.cap = capacity
        self.d: OrderedDict[_T, None] = OrderedDict()

    def add(self, x: _T) -> None:
        if x in self.d:
            return
        elif len(self.d) >= self.cap:
            self.d.popitem(last=False)
        self.d[x] = None

    def __contains__(self, x: _T) -> bool:
        return x in self.d

    def __repr__(self) -> str:
        return str(self.d.keys())

    def __len__(self) -> int:
        return len(self.d)

    def as_set(self) -> set[_T]:
        return {k for k in self.d.keys()}
