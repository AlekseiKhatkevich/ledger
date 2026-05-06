from functools import cache

import msgspec

from api.user_asset_addresses.domain import UserAssetAddressData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetAddress
from logic.repositories.user_asser_address import BaseUserAssetAddressRepository
from sqlalchemy.dialects.postgresql import insert


@cache
class PostgresUserAssetAddressRepository(BaseUserAssetAddressRepository, PostgresBaseRepository):
    model = UserAssetAddress

    async def get_by_pubkey(self, pkey: str) -> UserAssetAddress:
        return await self.get_by_field_names(public_key=pkey)

    async def upsert(self, data: UserAssetAddressData) ->  int | None:
        insert_stmt = insert(self.model).values(msgspec.to_builtins(data))
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['user_id', 'public_key', ],
            set_=dict(
                public_key=insert_stmt.excluded.public_key,
                wallet_name=insert_stmt.excluded.wallet_name,
            ),
            where=self.model.public_key.is_distinct_from(insert_stmt.excluded.public_key) &
            self.model.wallet_name.is_distinct_from(insert_stmt.excluded.wallet_name),
        ).returning(self.model.id)

        async with self.db.session() as session:
            resp = await session.scalar(on_conflict_stmt)
            await session.commit()
        return resp