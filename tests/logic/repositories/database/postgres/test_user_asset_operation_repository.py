from typing import Iterable

import pytest

from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import UserAssetAddress, AssetTicker, UserAsset, AssetOperationType
from tests.logic.db_models.factories import (
    UserAssetAddressFactory,
    UserAssetFactory,
    AssetTickerFactory,
    UserAssetOperationFactory,
)
from user.domain import User


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
        db,
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
):
    operations = []
    for user_asset, address in zip(user_asset_in_db_many, user_asset_address_in_db_many):
        operations.append(
            user_asset_operation_factory.build(
                type=AssetOperationType.PURCHASE,
                user_asset_id=user_asset.id,
                address_id=address.id,
            )
        )
        operations.append(
            user_asset_operation_factory.build(
                type=AssetOperationType.SELL,
                user_asset_id=user_asset.id,
                quantity=0.1,
                address_id=address.id,
            )
        )
    return await pg_user_asset_operation_repo.add_all(operations)

async def test_get_user_asset_aggregates_positive(user_asset_operations_in_db_many):
    pass
