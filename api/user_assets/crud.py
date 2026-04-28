from litestar import Controller, route
from litestar.dto import DTOData

from api.user_assets.domain import UserAssetData, UserAssetDto
from logic.usecases.user_asset_upsert import UserAssetUpsertUseCase
from user.domain import User


class UserAssetCrudController(Controller):
    path = '/user_asset'
    tags = ('user_asset', 'user_asset_crud', )

    @route('/', dto=UserAssetDto, http_method=["POST", "PUT", "PATCH"])
    async def create_or_update(self, data: DTOData[UserAssetData], kc_user: User) -> UserAssetData:
        user_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetUpsertUseCase().execute(user_data)
        return user_data
