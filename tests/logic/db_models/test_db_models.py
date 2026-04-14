from tests.logic.db_models.factories import UserAssetAddressFactory
from database.postgres.connection import db


async def test_user_asset_address_positive(
        user_asset_address_factory,
        user_asset_address_factory_in_db,
):
    # UserAssetAddressFactory.__async_session__ = db.session
    #
    # address = await UserAssetAddressFactory.create_async()
    pass