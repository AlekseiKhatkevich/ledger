import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.db_models import AssetTicker


class BaseAssetTickerRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_name(self, name: str) -> AssetTicker:
        pass