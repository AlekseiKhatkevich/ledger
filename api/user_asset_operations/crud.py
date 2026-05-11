from litestar import Controller, post
from litestar.dto import DTOData

from api.user_asset_operations.domain import (
    UserAssetOperationData,
    UserAssetOperationDTOOut,
    UserAssetOperationDTOIn,
)
from logic.usecases.user_asset_operation import UserAssetOperationUseCase
from user.domain import User


class UserAssetAddressOperationController(Controller):
    path = 'user_asset_operations'
    tags = ('user_asset_operations', )
# todo exception handling, maybe move all handlers into a separate router
    @post(
        '/',
        dto=UserAssetOperationDTOIn,
        return_dto=UserAssetOperationDTOOut,
    )
    async def create(self, data: DTOData[UserAssetOperationData], kc_user: User) -> UserAssetOperationData:
        user_asset_operation_data = data.create_instance(user_id=kc_user.sub)
        return await UserAssetOperationUseCase().execute(user_asset_operation_data)