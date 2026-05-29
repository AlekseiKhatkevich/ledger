import abc

from logic.db_models import AssetTickerPrice


class BaseAssetTickerPriceRepository(abc.ABC):

    @abc.abstractmethod
    async def get_prices(self, names: set[str]) -> list[AssetTickerPrice]:
        ...