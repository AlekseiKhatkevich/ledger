from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetAddress
from logic.repositories.user_asser_address import BaseUserAssetAddressRepository


@cache
class PostgresUserAssetAddressRepository(BaseUserAssetAddressRepository, PostgresBaseRepository):
    model = UserAssetAddress

    async def get_by_pubkey(self, pkey: str) -> UserAssetAddress:
        return await self.get_by_field_names(public_key=pkey)