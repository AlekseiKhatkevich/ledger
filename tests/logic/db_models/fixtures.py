import datetime
import decimal
import uuid
from typing import TYPE_CHECKING, Iterable

import pytest
from polyfactory.pytest_plugin import register_fixture

import constants
from database.postgres.repositories.asset_popularity import PostgresPopularityRepository
from database.postgres.repositories.asset_ticker import PostgresAssetTickerRepository
from database.postgres.repositories.asset_ticker_price import PostgresAssetTickerPriceRepository
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_address import PostgresUserAssetAddressRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import AssetOperationType, AssetTickerPrice
from tests.logic.db_models.factories import (
    UserAssetAddressFactory,
    AssetTickerFactory,
    UserAssetFactory,
    UserAssetOperationFactory,
    AssetTickerPriceFactory,
)
from user.domain import User

if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress, AssetTicker, UserAsset, UserAssetOperation

register_fixture(UserAssetAddressFactory)
register_fixture(AssetTickerFactory)
register_fixture(UserAssetFactory)
register_fixture(UserAssetOperationFactory)
register_fixture(AssetTickerPriceFactory)


@pytest.fixture(scope='session')
def pg_user_asset_address_repo() -> PostgresUserAssetAddressRepository:
    return PostgresUserAssetAddressRepository()

@pytest.fixture(scope='session')
def pg_asset_ticker_repo() -> PostgresAssetTickerRepository:
    return PostgresAssetTickerRepository()

@pytest.fixture(scope='session')
def pg_user_asset_repo() -> PostgresUserAssetRepository:
    return PostgresUserAssetRepository()

@pytest.fixture(scope='session')
def pg_asset_ticker_price_repo() -> PostgresAssetTickerPriceRepository:
    return PostgresAssetTickerPriceRepository()

@pytest.fixture(scope='session')
def pg_user_asset_operation_repo() -> PostgresUserAssetOperationRepository:
    return PostgresUserAssetOperationRepository()

@pytest.fixture(scope='session')
def pg_asset_popularity_repo() -> PostgresPopularityRepository:
    return PostgresPopularityRepository()


@pytest.fixture
async def asset_ticker_price_in_db(
        request,
        asset_ticker_price_factory: AssetTickerPriceFactory,
        asset_ticker_in_db: AssetTicker,
) -> AssetTickerPrice:
    outdated = hasattr(request, 'param') and request.param == 'outdated'
    kwargs = {'name': asset_ticker_in_db.name}
    if outdated:
        kwargs['updated_at'] = datetime.datetime.now(tz=datetime.UTC) - \
                                datetime.timedelta(minutes=constants.ASSET_PRICE_CONSIDER_STALE_AFTER * 2)

    return await asset_ticker_price_factory.create_async(**kwargs)

@pytest.fixture
async def user_asset_address_in_db(
        user_asset_address_factory: UserAssetAddressFactory,
        jwt_user:User,
) -> UserAssetAddress:
    return await user_asset_address_factory.create_async(user_id=jwt_user.sub)

@pytest.fixture
async def asset_ticker_in_db(asset_ticker_factory: AssetTickerFactory) -> AssetTicker:
    return await asset_ticker_factory.create_async()

@pytest.fixture
async def user_asset_in_db(
        user_asset_factory: UserAssetFactory,
        asset_ticker_in_db: AssetTicker,
        jwt_user: User,
) -> UserAsset:
    return await user_asset_factory.create_async(
        ticker_id=asset_ticker_in_db.name,
        user_id=jwt_user.id,
    )

@pytest.fixture
async def user_asset_operation_in_db(
        user_asset_operation_factory: UserAssetOperationFactory,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db:UserAssetAddress,
) -> UserAssetOperation:
    return await user_asset_operation_factory.create_async(
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )


@pytest.fixture
async def purchase_operation_in_db(
        user_asset_operation_factory: UserAssetOperationFactory,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
) -> UserAssetOperation:
    return await user_asset_operation_factory.create_async(
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
        type=AssetOperationType.PURCHASE,
    )

@pytest.fixture
async def user_asset_address_in_db_many(
        user_asset_address_factory: UserAssetAddressFactory,
        jwt_user: User,
) -> list[UserAssetAddress]:
    return await user_asset_address_factory.create_batch_async(size=10, user_id=jwt_user.sub)


@pytest.fixture
async def user_asset_ticker_in_db_many(
    asset_ticker_factory: AssetTickerFactory,
) -> list[AssetTicker]:
    return await asset_ticker_factory.create_batch_async(size=5)


@pytest.fixture
async def user_asset_in_db_many(
        user_asset_factory: UserAssetFactory,
        user_asset_ticker_in_db_many: list[AssetTicker],
        pg_user_asset_repo: PostgresUserAssetRepository ,
        jwt_user: User,
) -> Iterable[UserAsset]:
    user_assets = [
        user_asset_factory.build(user_id=jwt_user.sub, ticker_id=ticker.name)
        for ticker in user_asset_ticker_in_db_many
    ]
    return await pg_user_asset_repo.add_all(user_assets)


@pytest.fixture
async def user_asset_operations_in_db_many(
        user_asset_in_db_many: list[UserAsset],
        user_asset_operation_factory: UserAssetOperationFactory,
        user_asset_address_in_db_many: list[UserAssetAddress],
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
) -> list[UserAssetOperation] :
    operations = []
    for user_asset, address in zip(user_asset_in_db_many, user_asset_address_in_db_many):
        operations.append(
            purchase_operation := user_asset_operation_factory.build(
                type=AssetOperationType.PURCHASE,
                user_asset_id=user_asset.id,
                address_id=address.id,
            )
        )
        operations.append(
            user_asset_operation_factory.build(
                type=AssetOperationType.SELL,
                user_asset_id=user_asset.id,
                quantity=purchase_operation.quantity - decimal.Decimal(0.7),
                address_id=address.id,
            )
        )
    return await pg_user_asset_operation_repo.add_all(operations)


@pytest.fixture
async def extra_user_asset_in_db_full_monty(
        asset_ticker_in_db: AssetTicker,
        user_asset_factory: UserAssetFactory,
        user_asset_operation_factory: UserAssetOperationFactory,
        user_asset_address_in_db: UserAssetAddress,
) -> tuple[UserAsset, UserAssetOperation]:
    extra_user_asset = await user_asset_factory.create_async(
        ticker_id=asset_ticker_in_db.name,
        user_id=uuid.uuid7(),
    )
    extra_user_asset_operation = await user_asset_operation_factory.create_async(
        user_asset_id=extra_user_asset.id,
        address_id=user_asset_address_in_db.id,
    )
    return extra_user_asset, extra_user_asset_operation
