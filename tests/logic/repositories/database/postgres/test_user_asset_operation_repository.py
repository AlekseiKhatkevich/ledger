import decimal
import uuid
from typing import Iterable

import pytest
from sqlalchemy import func, select

from api.user_asset_operations.domain import DbCRUDOperationReturnData
from api.user_assets.domain import UserAssetAggregatedPage
from database.postgres.connection import db
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


# ───────── Fixtures for insert/update/delete tests ─────────


@pytest.fixture
async def second_user_asset_in_db(
        user_asset_factory: UserAssetFactory,
        asset_ticker_in_db: AssetTicker,
) -> UserAsset:
    """UserAsset belonging to another (non-jwt) user."""
    return await user_asset_factory.create_async(
        ticker_id=asset_ticker_in_db.name,
        user_id=uuid.uuid7(),
    )


@pytest.fixture
async def second_user_asset_address_in_db(
        user_asset_address_factory: UserAssetAddressFactory,
) -> UserAssetAddress:
    """UserAssetAddress belonging to another (non-jwt) user."""
    return await user_asset_address_factory.create_async(user_id=uuid.uuid7())


# ───────── End fixtures ─────────


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
    extra_user_asset, _ = extra_user_asset_in_db_full_monty

    user_assets_agg = await pg_user_asset_operation_repo.get_user_asset_aggregates(
        user_id=jwt_user.id,
        page_size=9999,
        cursor=None,
    )
    assert extra_user_asset.id not in {ua.id for ua in user_assets_agg.items}
    assert len(user_assets_agg.items) == len(user_asset_operations_in_db_many) / 2


# ═══════════════════════════════════════════════════════
# insert_if_valid tests
# ═══════════════════════════════════════════════════════

async def test_insert_if_valid_purchase_positive(
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """A PURCHASE operation should always succeed regardless of balance."""
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
        id=None,
    )

    result = await pg_user_asset_operation_repo.insert_if_valid(data)

    assert result == DbCRUDOperationReturnData(
        id=result.id,
        asset_exists=True,
        address_exists=True,
        balance=decimal.Decimal(0),
        balance_ok=True,
    )
    assert result.id is not None

    # Verify the operation was actually inserted in the database
    created_operation = await pg_user_asset_operation_repo.get_by_id(result.id)
    assert created_operation is not None
    assert created_operation.type == data.type
    assert created_operation.quantity == data.quantity
    assert created_operation.unit_price == data.unit_price
    assert created_operation.user_asset_id == data.user_asset_id
    assert created_operation.address_id == data.address_id


async def test_insert_if_valid_sell_enough_balance(
        purchase_operation_in_db: UserAssetOperation,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """A SELL with quantity <= balance after a purchase should succeed."""
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.SELL,
        quantity=purchase_operation_in_db.quantity,
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
        id=None,
    )

    result = await pg_user_asset_operation_repo.insert_if_valid(data)

    assert result.asset_exists is True
    assert result.address_exists is True
    assert result.balance_ok is True
    assert result.id is not None

    # Verify the operation was actually inserted in the database
    created_operation = await pg_user_asset_operation_repo.get_by_id(result.id)
    assert created_operation is not None
    assert created_operation.type == data.type
    assert created_operation.quantity == data.quantity
    assert created_operation.unit_price == data.unit_price
    assert created_operation.user_asset_id == data.user_asset_id
    assert created_operation.address_id == data.address_id


async def test_insert_if_valid_asset_not_exists(
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """Insert with a non-existent user_asset_id for this user should fail."""
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=999999,
        address_id=user_asset_address_in_db.id,
        id=None,
    )

    result = await pg_user_asset_operation_repo.insert_if_valid(data)

    assert result == DbCRUDOperationReturnData(
        id=None,
        asset_exists=False,
        address_exists=True,
        balance=decimal.Decimal(0),
        balance_ok=True,
    )

    # Verify no new operation was created in the database
    async with db.session() as session:
        count = await session.scalar(
            select(func.count()).select_from(UserAssetOperation)
            .where(UserAssetOperation.user_asset_id == 999999)
        )
    assert count == 0


async def test_insert_if_valid_address_not_exists(
        user_asset_in_db: UserAsset,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """Insert with a non-existent address_id for this user should fail."""
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=999999,
        id=None,
    )

    result = await pg_user_asset_operation_repo.insert_if_valid(data)

    assert result == DbCRUDOperationReturnData(
        id=None,
        asset_exists=True,
        address_exists=False,
        balance=decimal.Decimal(0),
        balance_ok=True,
    )

    # Verify no new operation was created with the non-existent address
    async with db.session() as session:
        count = await session.scalar(
            select(func.count()).select_from(UserAssetOperation)
            .where(UserAssetOperation.address_id == 999999)
        )
    assert count == 0


async def test_insert_if_valid_sell_insufficient_balance(
        purchase_operation_in_db: UserAssetOperation,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """A SELL with quantity > balance should fail with balance_ok=False."""
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.SELL,
        quantity=purchase_operation_in_db.quantity * 100,  # way more than the purchase
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
        id=None,
    )

    # Count existing operations for this (address, asset) pair before the attempt
    async with db.session() as session:
        count_before = await session.scalar(
            select(func.count()).select_from(UserAssetOperation)
            .where(
                UserAssetOperation.address_id == data.address_id,
                UserAssetOperation.user_asset_id == data.user_asset_id,
            )
        )

    result = await pg_user_asset_operation_repo.insert_if_valid(data)

    assert result.asset_exists is True
    assert result.address_exists is True
    assert result.balance_ok is False
    assert result.id is None

    # Verify no new operation was inserted
    async with db.session() as session:
        count_after = await session.scalar(
            select(func.count()).select_from(UserAssetOperation)
            .where(
                UserAssetOperation.address_id == data.address_id,
                UserAssetOperation.user_asset_id == data.user_asset_id,
            )
        )
    assert count_after == count_before


# ═══════════════════════════════════════════════════════
# update_if_valid tests
# ═══════════════════════════════════════════════════════

async def test_update_if_valid_positive(
        purchase_operation_in_db: UserAssetOperation,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """Update a PURCHASE operation with new data should succeed."""
    new_qty = purchase_operation_in_db.quantity + decimal.Decimal(5)
    new_price = purchase_operation_in_db.unit_price + decimal.Decimal(5)

    data = user_asset_operation_data_factory.build(
        id=purchase_operation_in_db.id,
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        quantity=new_qty,
        unit_price=new_price,
        address_id=user_asset_address_in_db.id,
    )

    result = await pg_user_asset_operation_repo.update_if_valid(data)

    assert result.asset_exists is True
    assert result.address_exists is True
    assert result.balance_ok is True
    assert result.id == purchase_operation_in_db.id

    # Verify the operation was actually updated in the database
    updated_operation = await pg_user_asset_operation_repo.get_by_id(purchase_operation_in_db.id)
    assert updated_operation is not None
    assert updated_operation.quantity == new_qty
    assert updated_operation.unit_price == new_price


async def test_update_if_valid_sell_enough_balance_excluding_self(
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        user_asset_operation_factory: UserAssetOperationFactory,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """
    When updating a SELL, the operation being updated is excluded from balance.
    Create a purchase (10) + sell (6). Balance excluding the sell = 10.
    Updating the sell to qty=8 should succeed (8 <= 10).
    """
    purchase = await user_asset_operation_factory.create_async(
        type=AssetOperationType.PURCHASE,
        quantity=decimal.Decimal(10),
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    sell_op = await user_asset_operation_factory.create_async(
        type=AssetOperationType.SELL,
        quantity=decimal.Decimal(6),
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )

    data = user_asset_operation_data_factory.build(
        id=sell_op.id,
        type=AssetOperationType.SELL,
        quantity=decimal.Decimal(8),
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )

    result = await pg_user_asset_operation_repo.update_if_valid(data)

    assert result.asset_exists is True
    assert result.address_exists is True
    assert result.balance_ok is True
    assert result.id == sell_op.id

    # Verify the operation was actually updated in the database
    updated_operation = await pg_user_asset_operation_repo.get_by_id(sell_op.id)
    assert updated_operation is not None
    assert updated_operation.quantity == decimal.Decimal(8)


async def test_update_if_valid_asset_not_exists(
        user_asset_operation_in_db: UserAssetOperation,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """Update with a non-existent user_asset_id for this user should fail."""
    # Read the original operation state before the failed update
    original_operation = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)

    data = user_asset_operation_data_factory.build(
        id=user_asset_operation_in_db.id,
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=999999,
        address_id=user_asset_address_in_db.id,
    )

    result = await pg_user_asset_operation_repo.update_if_valid(data)

    assert result.asset_exists is False
    assert result.address_exists is True
    assert result.id is None

    # Verify the operation was NOT modified in the database
    unchanged_operation = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)
    assert unchanged_operation is not None
    assert unchanged_operation.quantity == original_operation.quantity
    assert unchanged_operation.unit_price == original_operation.unit_price
    assert unchanged_operation.type == original_operation.type
    assert unchanged_operation.user_asset_id == original_operation.user_asset_id
    assert unchanged_operation.address_id == original_operation.address_id


async def test_update_if_valid_address_not_exists(
        user_asset_operation_in_db: UserAssetOperation,
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """Update with a non-existent address_id for this user should fail."""
    # Read the original operation state before the failed update
    original_operation = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)

    data = user_asset_operation_data_factory.build(
        id=user_asset_operation_in_db.id,
        type=AssetOperationType.PURCHASE,
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=999999,
    )

    result = await pg_user_asset_operation_repo.update_if_valid(data)

    assert result.address_exists is False
    assert result.asset_exists is True
    assert result.id is None

    # Verify the operation was NOT modified in the database
    unchanged_operation = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)
    assert unchanged_operation is not None
    assert unchanged_operation.quantity == original_operation.quantity
    assert unchanged_operation.unit_price == original_operation.unit_price
    assert unchanged_operation.type == original_operation.type
    assert unchanged_operation.user_asset_id == original_operation.user_asset_id
    assert unchanged_operation.address_id == original_operation.address_id


async def test_update_if_valid_sell_insufficient_balance(
        user_asset_in_db: UserAsset,
        user_asset_address_in_db: UserAssetAddress,
        user_asset_operation_factory: UserAssetOperationFactory,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        user_asset_operation_data_factory,
        jwt_user: User,
):
    """
    Purchase (10) + sell (10). Balance excluding the sell = 10.
    Try to update the sell to qty=12 (>10) – should fail.
    """
    await user_asset_operation_factory.create_async(
        type=AssetOperationType.PURCHASE,
        quantity=decimal.Decimal(10),
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    sell_op = await user_asset_operation_factory.create_async(
        type=AssetOperationType.SELL,
        quantity=decimal.Decimal(10),
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )

    # Read the original operation state before the failed update
    original_operation = await pg_user_asset_operation_repo.get_by_id(sell_op.id)

    data = user_asset_operation_data_factory.build(
        id=sell_op.id,
        type=AssetOperationType.SELL,
        quantity=decimal.Decimal(12),
        user_id=jwt_user.sub,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )

    result = await pg_user_asset_operation_repo.update_if_valid(data)

    assert result.asset_exists is True
    assert result.address_exists is True
    assert result.balance_ok is False
    assert result.id is None

    # Verify the operation was NOT modified in the database
    unchanged_operation = await pg_user_asset_operation_repo.get_by_id(sell_op.id)
    assert unchanged_operation is not None
    assert unchanged_operation.quantity == original_operation.quantity


# ═══════════════════════════════════════════════════════
# delete_if_valid tests
# ═══════════════════════════════════════════════════════

async def test_delete_if_valid_positive(
        user_asset_operation_in_db: UserAssetOperation,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        jwt_user: User,
):
    """Delete an existing operation belonging to the current user should return its id."""

    # Verify the operation exists before deletion
    existing_operation = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)
    assert existing_operation is not None

    deleted_id = await pg_user_asset_operation_repo.delete_if_valid(
        _id=user_asset_operation_in_db.id,
        user_id=jwt_user.sub,
    )

    assert deleted_id == user_asset_operation_in_db.id

    # Verify the operation is actually deleted from the database
    fetched = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)
    assert fetched is None


async def test_delete_if_valid_not_exists(
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        jwt_user: User,
):
    """Delete a non-existent operation should return None."""
    deleted_id = await pg_user_asset_operation_repo.delete_if_valid(
        _id=999999,
        user_id=jwt_user.sub,
    )

    assert deleted_id is None


async def test_delete_if_valid_other_user(
        user_asset_operation_factory: UserAssetOperationFactory,
        second_user_asset_in_db: UserAsset,
        second_user_asset_address_in_db: UserAssetAddress,
        pg_user_asset_operation_repo: PostgresUserAssetOperationRepository,
        jwt_user: User,
):
    """Delete an operation belonging to another user should return None."""
    other_operation = await user_asset_operation_factory.create_async(
        user_asset_id=second_user_asset_in_db.id,
        address_id=second_user_asset_address_in_db.id,
    )

    # Verify the operation exists before the failed deletion
    existing_operation = await pg_user_asset_operation_repo.get_by_id(other_operation.id)
    assert existing_operation is not None

    deleted_id = await pg_user_asset_operation_repo.delete_if_valid(
        _id=other_operation.id,
        user_id=jwt_user.sub,
    )

    assert deleted_id is None

    # Verify the operation still exists in the database (not deleted by other user)
    fetched = await pg_user_asset_operation_repo.get_by_id(other_operation.id)
    assert fetched is not None