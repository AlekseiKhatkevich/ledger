import decimal
import uuid
from typing import Iterable

import pytest

from api.user_assets.domain import UserAssetAggregatedPage
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import (
    UserAssetAddress,
    AssetTicker,
    UserAsset,
    AssetOperationType,
    UserAssetOperation,
)
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


async def test_get_user_asset_aggregates_positive(
        user_asset_operations_in_db_many,
        pg_user_asset_operation_repo,
        jwt_user,
        user_asset_address_in_db_many,
        user_asset_in_db_many,
):
    user_assets_agg = await pg_user_asset_operation_repo.get_user_asset_aggregates(
        user_id=jwt_user.id,
        page_size=99999,
        cursor=None,
    )

    assert isinstance(user_assets_agg, UserAssetAggregatedPage)
    #  / 2 because of each pair of PURCHASE + SELL is grouped
    assert len(user_assets_agg.items) == len(user_asset_operations_in_db_many) / 2
    #  cursor is a last ticker_it of batch sorted lexicographically
    assert (user_assets_agg.cursor ==
            sorted(user_assets_agg.items, key= lambda x: x.ticker_id)[-1].ticker_id)
    assert not user_assets_agg.has_more

    for user_asset in user_assets_agg.items:
        our_operations = list(
            filter(lambda op: op.user_asset_id == user_asset.id, user_asset_operations_in_db_many)
        )
        expected_coin_qty = sum(
            (op.quantity if op.type == AssetOperationType.PURCHASE else - op.quantity for op in our_operations),
            start=decimal.Decimal(0)
        )
        assert user_asset.coin_qty_now == pytest.approx(expected_coin_qty)
        assert user_asset.unique_addresses_cnt == 1
        expected_purchased_for_usdt =  sum(
            (op.summ for op in our_operations if op.type == AssetOperationType.PURCHASE),
            start=decimal.Decimal(0)
        )
        assert user_asset.purchased_for_usdt == pytest.approx(expected_purchased_for_usdt)
        expected_sold_for_usdt = sum(
            (op.summ for op in our_operations if op.type == AssetOperationType.SELL),
            start=decimal.Decimal(0)
        )
        assert user_asset.sold_for_usdt == pytest.approx(expected_sold_for_usdt)
        expected_num_purchases = len(
            [op for op in our_operations if op.type == AssetOperationType.PURCHASE]
        )
        assert user_asset.num_purchases == expected_num_purchases
        expected_num_sales = len(
            [op for op in our_operations if op.type == AssetOperationType.SELL]
        )
        assert user_asset.num_sells == expected_num_sales
        addresses_dict = {addr.id: addr for addr in user_asset_address_in_db_many}
        user_asset_op_dict = {ua.user_asset_id: ua for ua in user_asset_operations_in_db_many}
        user_asset_in_op_in_db = user_asset_op_dict[user_asset.id]
        assert sorted(user_asset.wallet_names) == sorted(addresses_dict[user_asset_in_op_in_db.address_id].wallet_name)


async def test_get_user_asset_aggregates_positive_with_page_size(
        user_asset_operations_in_db_many,
        pg_user_asset_operation_repo,
        jwt_user,
):
    user_assets_agg = await pg_user_asset_operation_repo.get_user_asset_aggregates(
        user_id=jwt_user.id,
        page_size=1,
        cursor=None,
    )
    assert len(user_assets_agg.items) == 1
    assert user_assets_agg.cursor == user_assets_agg.items[0].ticker_id
    assert user_assets_agg.has_more


async def test_get_user_asset_aggregates_positive_with_cursor(
        user_asset_operations_in_db_many,
        pg_user_asset_operation_repo,
        jwt_user,
        user_asset_ticker_in_db_many,
):
    # we have 5 assets associated with 5 tickers. Sort them lexicographically and get one from the middle
    # then make it a cursor. Hence, we should get all assets with tickers behind this one.
    first, second, third, forth, fifth = sorted(user_asset_ticker_in_db_many, key=lambda t: t.name)
    user_assets_agg = await pg_user_asset_operation_repo.get_user_asset_aggregates(
        user_id=jwt_user.id,
        page_size=9999,
        cursor=third.name,
    )
    assert len(user_assets_agg.items) == 2
    assert {ua.ticker_id for ua in user_assets_agg.items} == {forth.name, fifth.name}
    assert not user_assets_agg.has_more


async def test_get_user_asset_aggregates_positive_with_extra_user_asset(
        user_asset_operations_in_db_many,
        pg_user_asset_operation_repo,
        jwt_user,
        extra_user_asset_in_db_full_monty,
):
    extra_user_asset, extra_user_asset_operation = extra_user_asset_in_db_full_monty

    user_assets_agg = await pg_user_asset_operation_repo.get_user_asset_aggregates(
        user_id=jwt_user.id,
        page_size=9999,
        cursor=None,
    )
    assert extra_user_asset.id not in {ua.id for ua in user_assets_agg.items}
    assert len(user_assets_agg.items) == len(user_asset_operations_in_db_many) / 2
