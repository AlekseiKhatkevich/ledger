import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.db_models import AssetPopularity


class BaseAssetPopularityRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_ticker_id(self, ticker_id: str) -> AssetPopularity:
        pass
