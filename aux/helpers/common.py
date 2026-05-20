from typing import Generator, Any


def iter_subclasses(cls) -> Generator[Any]:
        for sub in cls.__subclasses__():
            yield sub
            yield from iter_subclasses(sub)
