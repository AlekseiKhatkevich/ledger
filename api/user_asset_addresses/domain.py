from litestar import Controller, route


class UserAssetAddressController(Controller):
    path = 'user_asset_address'
    tags = ('user_asset_address', )

    @route('/', http_method=['POST', 'PUT'])
    async def create_or_update(self, data):
        pass