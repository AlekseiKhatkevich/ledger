from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.exceptions import UserAssetNotFoundError, UserAssetAddressNotFoundError, UserAssetOperationNotFoundError


def _check_asset_and_address(data: UserAssetOperationData, *, asset_exists: bool, address_exists: bool) -> None:
    if not asset_exists:
        raise UserAssetNotFoundError(extra={'id': data.user_asset_id})

    if not address_exists:
        raise UserAssetAddressNotFoundError(extra={'id': data.address_id})

def _check_if_updated(data: UserAssetOperationData, *, updated_id: int | None) -> None:
    if updated_id is None:
        raise UserAssetOperationNotFoundError(extra={'id': data.id})


class UserAssetOperationInsertUseCase:

    @staticmethod
    async def execute(data: UserAssetOperationData) -> UserAssetOperationData:
        inserted_id, asset_exists, address_exists = await PostgresUserAssetOperationRepository().insert_if_valid(data)

        _check_asset_and_address(data, asset_exists=asset_exists, address_exists=address_exists)

        data.id = inserted_id

        return data


class UserAssetOperationUpdateUseCase:

    @staticmethod
    async def execute(data: UserAssetOperationData) -> UserAssetOperationData:
        updated_id, asset_exists, address_exists = await PostgresUserAssetOperationRepository().update_if_valid(data)

        _check_asset_and_address(data, asset_exists=asset_exists, address_exists=address_exists)
        _check_if_updated(data, updated_id=updated_id)

        return data
