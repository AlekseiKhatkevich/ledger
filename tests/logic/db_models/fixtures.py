from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from database.postgres.repositories.asset_ticker import PostgresAssetTickerRepository
from database.postgres.repositories.user_asser_address import PostgresUserAssetAddressRepository
from tests.logic.db_models.factories import UserAssetAddressFactory, AssetTickerFactory

if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress, AssetTicker

register_fixture(UserAssetAddressFactory)
register_fixture(AssetTickerFactory)


@pytest.fixture(scope='session')
def pg_user_asset_repo() -> PostgresUserAssetAddressRepository:
    return PostgresUserAssetAddressRepository()

@pytest.fixture(scope='session')
def pg_asset_ticker_repo() -> PostgresAssetTickerRepository:
    return PostgresAssetTickerRepository()

@pytest.fixture
async def user_asset_address_in_db(user_asset_address_factory: UserAssetAddressFactory) -> UserAssetAddress:
    return await user_asset_address_factory.create_async()

@pytest.fixture
async def asset_ticker_in_db(asset_ticker_factory: AssetTickerFactory) -> AssetTicker:
    return await asset_ticker_factory.create_async()
