import msgspec

from api.user_asset_addresses.domain import UserAssetAddressData, UserAssetAddressUpdateData
from database.postgres.repositories.user_asset_address import PostgresUserAssetAddressRepository
from logic.exceptions import UserAssetAddressNotFoundError


class UserAssetAddressInsertUseCase:

    @staticmethod
    async def execute(data: UserAssetAddressData) -> int | None:
        return await PostgresUserAssetAddressRepository().insert(data)


class UserAssetAddressUpdateUseCase:

    @staticmethod
    async def execute(data: UserAssetAddressUpdateData) -> UserAssetAddressData:
        instance = await PostgresUserAssetAddressRepository().update(data)
        if instance is not None:
            return msgspec.convert(instance.as_fields_dict(), type=UserAssetAddressData)
        else:
            raise UserAssetAddressNotFoundError()
