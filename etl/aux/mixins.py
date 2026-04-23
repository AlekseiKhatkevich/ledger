import abc


class Finalizable(abc.ABC):

    @property
    @abc.abstractmethod
    async def finalize(self) -> None:
        pass
