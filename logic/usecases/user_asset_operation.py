import uuid

from api.user_asset_operations.domain import (
    UserAssetOperationData,
    DbCRUDOperationReturnData,
    UserAssetOperationsFilter,
    NettoPositionData, UserAssetOperationWithNotesOut,
)
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

def _check_if_deleted(_id: int, *, deleted_id: int | None) -> None:
    if deleted_id is None:
        raise UserAssetOperationNotFoundError(extra={'id': _id})

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


class UserAssetOperationDeleteUseCase:

    @staticmethod
    async def execute(_id: int, user_id: uuid.UUID) -> None:
        deleted_id = await PostgresUserAssetOperationRepository().delete_if_valid(_id, user_id)
        _check_if_deleted(_id, deleted_id=deleted_id)


class UserAssetOperationNettoPositionUseCase:

    @staticmethod
    async def execute(
            user_asset_id: int,
            user_id: uuid.UUID,
            op_filter: UserAssetOperationsFilter,
    ) -> NettoPositionData | None:
        return await PostgresUserAssetOperationRepository().netto_position(
            user_asset_id=user_asset_id,
            user_id=user_id,
            op_filter=op_filter,
        )

class UserAssetOperationsByNotesUseCase:

    @staticmethod
    async def execute(
        user_id: uuid.UUID,
        op_filter: UserAssetOperationsFilter,
        notes: list[str],
        distance: int,
    ) -> list[UserAssetOperationWithNotesOut]:
        return await PostgresUserAssetOperationRepository().get_by_notes(
            user_id,
            op_filter,
            notes,
            distance,
        )
