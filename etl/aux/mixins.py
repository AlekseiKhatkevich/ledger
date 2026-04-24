import abc


class Finalizable(abc.ABC):

    @abc.abstractmethod
    async def finalize(self) -> None:
        pass
