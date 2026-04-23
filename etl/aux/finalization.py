from typing import Generator, Any, Type


def iter_subclasses(cls) -> Generator[Type[Any]]:
        for sub in cls.__subclasses__():
            yield sub
            yield from iter_subclasses(sub)
