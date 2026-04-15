from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from database.postgres.connection import db as _db, DB
from database.postgres.repositories.user_asser_address import PostgresUserAssetAddressRepository
from tests.logic.db_models.factories import UserAssetAddressFactory

if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress


register_fixture(UserAssetAddressFactory)


@pytest.fixture(scope='session')
def db() -> DB:
    return _db

@pytest.fixture(scope='session')
def pg_user_asset_repo() -> PostgresUserAssetAddressRepository:
    return PostgresUserAssetAddressRepository()

@pytest.fixture
async def user_asset_address_in_db(user_asset_address_factory: UserAssetAddressFactory) -> UserAssetAddress:
    return await user_asset_address_factory.create_async()