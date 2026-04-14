import pytest
from polyfactory.pytest_plugin import register_fixture
from database.postgres.connection import db as _db, DB
from tests.logic.db_models.factories import UserAssetAddressFactory

register_fixture(UserAssetAddressFactory)


@pytest.fixture(scope='session')
def db() -> DB:
    return _db

@pytest.fixture
async def user_asset_address_factory_in_db(
        user_asset_address_factory: UserAssetAddressFactory,
        db: DB,
):
    # noinspection PyClassVar
    user_asset_address_factory.__async_session__ = db.session
    return await user_asset_address_factory.create_async()