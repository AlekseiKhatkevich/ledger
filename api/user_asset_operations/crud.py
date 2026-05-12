from litestar import Controller, post
from litestar.dto import DTOData

from api.exceptions_handling import asset_not_found_error_handler_factory
from api.user_asset_operations.domain import (
    UserAssetOperationData,
    UserAssetOperationDTOOut,
    UserAssetOperationDTOIn,
)
from logic.exceptions import UserAssetNotFoundError, UserAssetAddressNotFoundError
from logic.usecases.user_asset_operation import UserAssetOperationUseCase
from user.domain import User


class UserAssetAddressOperationController(Controller):
    path = 'user_asset_operations'
    tags = ('user_asset_operations', )
    exception_handlers = {
        UserAssetNotFoundError: asset_not_found_error_handler_factory(
            'User asset does not not exists',
            'User asset with this user_asset_id does not exists for this user',
            'user_asset_not_exists.html',
        ),
        UserAssetAddressNotFoundError: asset_not_found_error_handler_factory(
            'Public key does not exists',
            'Public key can not be updated as it does not exists. You need to create it first',
            'user_asset_address_not_exists.html',
        )
    }
    @post(
        '/',
        dto=UserAssetOperationDTOIn,
        return_dto=UserAssetOperationDTOOut,
    )
    async def create(self, data: DTOData[UserAssetOperationData], kc_user: User) -> UserAssetOperationData:
        user_asset_operation_data = data.create_instance(user_id=kc_user.sub)
        return await UserAssetOperationUseCase().execute(user_asset_operation_data)