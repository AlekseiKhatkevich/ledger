from collections import OrderedDict
from typing import Hashable


class FixedSizeSet:
    def __init__(self, capacity:int = 100) -> None:
        self.cap = capacity
        self.d = OrderedDict()

    def add(self, x: Hashable) -> None:
        if x in self.d:
            return
        elif len(self.d) >= self.cap:
            self.d.popitem(last=False)
        self.d[x] = None

    def __contains__(self, x: Hashable) -> bool:
        return x in self.d

    def __repr__(self) -> str:
        return str(self.d.keys())

    def __len__(self) -> int:
        return len(self.d)

    def as_set(self) -> set[Hashable]:
        return {k for k in self.d.keys()}
