from api.user_asset_addresses.domain import UserAssetAddressData, UserAssetAddressUpdateData, UserAssetAddressDeleteData
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
            return instance.to_msgspec(type_=UserAssetAddressData)
        else:
            raise UserAssetAddressNotFoundError(extra={'public_key': data.public_key})


class UserAssetDeleteUseCase:

    @staticmethod
    async def execute(data: UserAssetAddressDeleteData) -> None:
        instance_id = await PostgresUserAssetAddressRepository().delete(data)
        if instance_id is not None:
            return None
        else:
            raise UserAssetAddressNotFoundError(extra={'public_key': data.public_key})