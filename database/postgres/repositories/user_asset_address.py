from functools import cache

import msgspec
from sqlalchemy import update

from api.user_asset_addresses.domain import UserAssetAddressData, UserAssetAddressUpdateData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetAddress
from logic.repositories.user_asser_address import BaseUserAssetAddressRepository
from sqlalchemy.dialects.postgresql import insert


@cache
class PostgresUserAssetAddressRepository(BaseUserAssetAddressRepository, PostgresBaseRepository):
    model = UserAssetAddress

    async def get_by_pubkey(self, pkey: str) -> UserAssetAddress:
        return await self.get_by_field_names(public_key=pkey)

    async def insert(self, data: UserAssetAddressData) ->  int | None:
        insert_stmt = insert(self.model).values(msgspec.to_builtins(data))
        on_conflict_stmt = insert_stmt.on_conflict_do_nothing(
            index_elements=['user_id', 'public_key', ],
        ).returning(
            self.model.id,
        )

        async with self.db.session() as session:
            resp = await session.scalar(on_conflict_stmt)
            await session.commit()
        return resp

    async def update(self, data: UserAssetAddressUpdateData) -> int | None:
        update_stmt = update(
            self.model
        ).where(
            self.model.user_id == data.new_data.user_id,
            self.model.public_key == data.public_key,
        ).values(
            msgspec.to_builtins(data.new_data),
        ).returning(
            self.model,
        )

        async with self.db.session() as session:
            resp = await session.scalar(update_stmt)
            await session.commit()
        return resp