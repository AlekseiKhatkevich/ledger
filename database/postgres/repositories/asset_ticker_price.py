from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import AssetTickerPrice
from logic.repositories.asset_ticer_price import BaseAssetTickerPriceRepository


@cache
class PostgresAssetTickerPriceRepository(
    PostgresBaseRepository[AssetTickerPrice],
    BaseAssetTickerPriceRepository,
):
    model = AssetTickerPrice
