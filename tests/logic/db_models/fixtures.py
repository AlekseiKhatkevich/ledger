from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from database.postgres.repositories.asset_ticker import PostgresAssetTickerRepository
from database.postgres.repositories.user_asset_address import PostgresUserAssetAddressRepository

from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from tests.logic.db_models.factories import UserAssetAddressFactory, AssetTickerFactory, UserAssetFactory

if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress, AssetTicker

register_fixture(UserAssetAddressFactory)
register_fixture(AssetTickerFactory)
register_fixture(UserAssetFactory)


@pytest.fixture(scope='session')
def pg_user_asset_address_repo() -> PostgresUserAssetAddressRepository:
    return PostgresUserAssetAddressRepository()

@pytest.fixture(scope='session')
def pg_asset_ticker_repo() -> PostgresAssetTickerRepository:
    return PostgresAssetTickerRepository()

@pytest.fixture(scope='session')
def pg_user_asset_repo() -> PostgresUserAssetRepository:
    return PostgresUserAssetRepository()

@pytest.fixture
async def user_asset_address_in_db(user_asset_address_factory: UserAssetAddressFactory) -> UserAssetAddress:
    return await user_asset_address_factory.create_async()

@pytest.fixture
async def asset_ticker_in_db(asset_ticker_factory: AssetTickerFactory) -> AssetTicker:
    return await asset_ticker_factory.create_async()

@pytest.fixture
async def user_asset_in_db(user_asset_factory: UserAssetFactory, asset_ticker_in_db):
    return await user_asset_factory.create_async(ticker_id=asset_ticker_in_db.name)
