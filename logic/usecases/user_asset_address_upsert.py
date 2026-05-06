from api.user_asset_addresses.domain import UserAssetAddressData
from database.postgres.repositories.user_asset_address import PostgresUserAssetAddressRepository


class UserAssetAddressUpsertUseCase:

    @staticmethod
    async def execute(data: UserAssetAddressData) -> int | None:
        return await PostgresUserAssetAddressRepository().upsert(data)