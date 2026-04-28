from dataclasses import asdict
from functools import cache

from sqlalchemy.dialects.postgresql import insert

from api.user_assets.domain import UserAssetData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAsset
from logic.repositories.user_asset import BaseUserAssetRepository


@cache
class PostgresUserAssetRepository(PostgresBaseRepository, BaseUserAssetRepository):
    model = UserAsset

    async def upsert(self, data: UserAssetData) -> None:
        insert_stmt = insert(self.model).values(**asdict(data))
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['user_id', 'ticker_id',],
            set_=dict(name=insert_stmt.excluded.name),
            where=self.model.name.is_distinct_from(insert_stmt.excluded.name),
        )
        async with self.db.session() as session:
            await session.execute(on_conflict_stmt)
            await session.commit()
