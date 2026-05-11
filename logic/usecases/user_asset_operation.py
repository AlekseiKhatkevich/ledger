from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.exceptions import UserAssetNotFoundError, UserAssetAddressNotFoundError


class UserAssetOperationUseCase:

    @staticmethod
    async def execute(data: UserAssetOperationData) -> UserAssetOperationData:
        inserted_id, asset_exists, address_exists = await PostgresUserAssetOperationRepository().insert_if_valid(data)

        if not asset_exists:
            raise UserAssetNotFoundError(extra={'id': data.user_asset_id})

        if not address_exists:
            raise UserAssetAddressNotFoundError(extra={'id': data.address_id})

        data.id = inserted_id

        return data
