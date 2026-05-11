from functools import cache

from sqlalchemy import exists, select

from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetOperation, UserAsset, UserAssetAddress
from logic.repositories.user_asset_operation import BaseUserAssetOperationRepository


@cache
class PostgresUserAssetOperationRepository(PostgresBaseRepository, BaseUserAssetOperationRepository):
    model = UserAssetOperation


    async def check_asset_and_address_exists(self, data: UserAssetOperationData) -> tuple[bool, bool]:
        asset_exists_stmt = exists().where(
            UserAsset.user_id == data.user_id,
            UserAsset.id == data.user_asset_id,
        )
        address_exists_stmt = exists().where(
            UserAssetAddress.user_id == data.user_id,
            UserAssetAddress.id == data.address_id,
        )
        async with self.db.session() as session:
            resp = await session.execute(select(asset_exists_stmt, address_exists_stmt))
            return resp.one_or_none()
