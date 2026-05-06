from litestar import Controller, route
from litestar.dto import DTOData

from api.user_asset_addresses.domain import UserAssetAddressData, UserAssetAddressDto
from logic.usecases.user_asset_address_upsert import UserAssetAddressUpsertUseCase
from user.domain import User


class UserAssetAddressController(Controller):
    path = 'user_asset_address'
    tags = ('user_asset_address', )

    @route(
        '/',
        http_method=['POST', 'PUT'],
        dto=UserAssetAddressDto
    )
    async def create_or_update(self, data: DTOData[UserAssetAddressData], kc_user: User) -> UserAssetAddressData:
        user_asset_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetAddressUpsertUseCase().execute(user_asset_data)
        return user_asset_data