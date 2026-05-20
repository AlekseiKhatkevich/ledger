from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import AssetPopularity
from logic.repositories.asset_popularity import BaseAssetPopularityRepository


@cache
class PostgresPopularityRepository(
    PostgresBaseRepository[AssetPopularity],
    BaseAssetPopularityRepository,
):
    model = AssetPopularity

    async def get_by_ticker_id(self, ticker_id: str) -> AssetPopularity:
        return await self.get_by_field_names(ticker_id=ticker_id)
