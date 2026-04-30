from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import AssetTicker
from logic.repositories.asset_ticker import BaseAssetTickerRepository


@cache
class PostgresAssetTickerRepository(BaseAssetTickerRepository, PostgresBaseRepository):
    model = AssetTicker

    async def get_by_name(self, name: str) -> AssetTicker:
        return await self.get_by_field_names(field_name='name', value=name)
