from api.user_asset_operations.domain import UserAssetOperationData, DbCRUDOperationReturnData
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.exceptions import (
    UserAssetNotFoundError,
    UserAssetAddressNotFoundError,
    UserAssetOperationNotFoundError,
    NotEnoughBalanceToSell,
)


def _check_asset_and_address(*, data: UserAssetOperationData, return_data: DbCRUDOperationReturnData) -> None:
    if not return_data.asset_exists:
        raise UserAssetNotFoundError(extra={'id': data.user_asset_id})

    if not return_data.address_exists:
        raise UserAssetAddressNotFoundError(extra={'id': data.address_id})

def _check_if_updated(*, data: UserAssetOperationData, return_data: DbCRUDOperationReturnData) -> None:
    if return_data.id is None:
        raise UserAssetOperationNotFoundError(extra={'id': data.id})

def _check_balance(return_data: DbCRUDOperationReturnData) -> None:
    if not return_data.balance_ok:
        raise NotEnoughBalanceToSell(extra={'current_balance': return_data.balance})


class UserAssetOperationInsertUseCase:

    @staticmethod
    async def execute(data: UserAssetOperationData) -> UserAssetOperationData:
        return_data = await PostgresUserAssetOperationRepository().insert_if_valid(data)

        _check_asset_and_address(data=data, return_data=return_data)
        _check_balance(return_data=return_data)

        data.id = return_data.id

        return data


class UserAssetOperationUpdateUseCase:

    @staticmethod
    async def execute(data: UserAssetOperationData) -> UserAssetOperationData:
        return_data = await PostgresUserAssetOperationRepository().update_if_valid(data)

        _check_asset_and_address(data=data, return_data=return_data)
        _check_balance(return_data=return_data)
        _check_if_updated(data=data, return_data=return_data)

        return data
