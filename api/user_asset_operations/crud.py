from litestar import Controller, post
from litestar.dto import DTOData

from api.user_asset_operations.domain import (
    UserAssetOperationData,
    UserAssetOperationDTOOut,
    UserAssetOperationDTOIn,
)
from user.domain import User


class UserAssetAddressOperationController(Controller):
    path = 'user_asset_operations'
    tags = ('user_asset_operations', )


    @post(
        '/',
        dto=UserAssetOperationDTOIn,
        return_dto=UserAssetOperationDTOOut,
    )
    async def create(self, data: DTOData[UserAssetOperationData], kc_user: User) -> UserAssetOperationData:
        user_asset_operation_data = data.create_instance(user_id=kc_user.sub)
        return user_asset_operation_data