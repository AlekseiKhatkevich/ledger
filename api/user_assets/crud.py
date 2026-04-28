from litestar import post, Controller
from litestar.dto import DTOData

from api.user_assets.domain import  UserAsset, UserAssetDto
from user.domain import User


class UserAssetCrudController(Controller):
    path = '/user_asset'
    tags = ('user_asset', 'user_asset_crud', )

    @post('/', dto=UserAssetDto)
    async def create_or_update(self, data: DTOData[UserAsset], kc_user: User) -> UserAsset:
        return data.create_instance(user_id=kc_user.sub)