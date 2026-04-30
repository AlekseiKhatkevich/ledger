from functools import cache

import msgspec
from sqlalchemy.dialects.postgresql import insert

from api.user_assets.domain import UserAssetData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAsset
from logic.repositories.user_asset import BaseUserAssetRepository


@cache
class PostgresUserAssetRepository(PostgresBaseRepository, BaseUserAssetRepository):
    model = UserAsset

    async def upsert(self, data: UserAssetData) ->  int | None:
        insert_stmt = insert(self.model).values(msgspec.to_builtins(data))
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['user_id', 'ticker_id',],
            set_=dict(name=insert_stmt.excluded.name),
            where=self.model.name.is_distinct_from(insert_stmt.excluded.name),
        ).returning(self.model.id)

        async with self.db.session() as session:
            resp = await session.scalar(on_conflict_stmt)
            await session.commit()
        return resp