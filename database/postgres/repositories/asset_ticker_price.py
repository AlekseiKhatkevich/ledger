import datetime
from functools import cache

from sqlalchemy import select, func
from sqlalchemy.orm import with_expression

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import AssetTickerPrice
from logic.repositories.asset_ticer_price import BaseAssetTickerPriceRepository


@cache
class PostgresAssetTickerPriceRepository(
    PostgresBaseRepository[AssetTickerPrice],
    BaseAssetTickerPriceRepository,
):
    model = AssetTickerPrice

    async def get_prices(self, names: set[str]) -> list[AssetTickerPrice]:
        stmt = select(self.model).options(
            with_expression(
                self.model.outdated,
                func.coalesce(
                    func.now() - self.model.updated_at > datetime.timedelta(minutes=5),
                    True,
                ),
            ),
        ).where(
            self.model.name.in_(names),
        )
        async with self.db.session() as session:
            res = await session.execute(stmt)
        return res.scalars().all()
        
