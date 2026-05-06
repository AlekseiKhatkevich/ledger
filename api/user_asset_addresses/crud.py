from litestar import Controller, post, put
from litestar.dto import DTOData

from api.user_asset_addresses.domain import (
    UserAssetAddressData,
    UserAssetAddressDto,
    UserAssetAddressUpdateData,
    UserAssetAddressUpdateDTOIn,
)
from logic.usecases.user_asset_address import UserAssetAddressUpdateUseCase, UserAssetAddressInsertUseCase
from user.domain import User


class UserAssetAddressController(Controller):
    path = 'user_asset_address'
    tags = ('user_asset_address', )

    @post(
        '/',
        dto=UserAssetAddressDto,
    )
    async def create(self, data: DTOData[UserAssetAddressData], kc_user: User) -> UserAssetAddressData:
        user_asset_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetAddressInsertUseCase().execute(user_asset_data)
        return user_asset_data

    @put(
        '/',
        dto=UserAssetAddressUpdateDTOIn,
        return_dto=UserAssetAddressDto,
    )
    async def update(self, data: DTOData[UserAssetAddressUpdateData], kc_user: User) -> UserAssetAddressData:
        user_asset_update_data = data.create_instance(new_data__user_id=kc_user.sub)
        return await UserAssetAddressUpdateUseCase.execute(user_asset_update_data)
# todo updata - update unique
# todo update - no public key , returns nothing