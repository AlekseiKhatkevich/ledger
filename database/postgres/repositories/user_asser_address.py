from sqlalchemy import select

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetAddress
from logic.repositories.user_asser_address import BaseUserAssetAddressRepository


class PostgresUserAssetAddressRepository(BaseUserAssetAddressRepository, PostgresBaseRepository):
    model = UserAssetAddress

    async def get_by_pubkey(self, pkey: str) -> UserAssetAddress:
        async  with self.db.session() as session:
            return await session.scalar(select(self.model).where(self.model.public_key == pkey))