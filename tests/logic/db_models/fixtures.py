from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from database.postgres.connection import db as _db, DB
from tests.logic.db_models.factories import UserAssetAddressFactory

if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress


register_fixture(UserAssetAddressFactory)


@pytest.fixture(scope='session')
def db() -> DB:
    return _db

@pytest.fixture
async def user_asset_address_factory_in_db(user_asset_address_factory: UserAssetAddressFactory) -> UserAssetAddress:
    return await user_asset_address_factory.create_async()