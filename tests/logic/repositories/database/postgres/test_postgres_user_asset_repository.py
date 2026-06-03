import datetime
import uuid

import pytest

import constants
from api.user_assets.domain import GetUserAssetDetailInputParams


async def test_postgres_user_asset_repository_create_positive(
        pg_user_asset_repo,
        asset_ticker_in_db,
        user_asset_data_factory,
):
    user_asset_data = user_asset_data_factory.build(ticker_id=asset_ticker_in_db.name)

    pk = await pg_user_asset_repo.upsert(user_asset_data)

    instance_from_db = await pg_user_asset_repo.get_by_id(pk)
    assert instance_from_db is not None


async def test_postgres_user_asset_repository_update_positive(
        pg_user_asset_repo,
        user_asset_in_db,
        user_asset_data_factory,
):
    user_asset_data = user_asset_data_factory.build(
        **user_asset_in_db.as_fields_dict(exclude={'id', 'name',}),
        name='new_test_name',
    )

    pk = await pg_user_asset_repo.upsert(user_asset_data)

    instance_from_db = await pg_user_asset_repo.get_by_id(pk)
    assert instance_from_db is not None


async def test_postgres_user_asset_repository_update_positive_do_nothing_on_same_data(
        pg_user_asset_repo,
        user_asset_in_db,
        user_asset_data_factory,
):
    user_asset_data = user_asset_data_factory.build(
        **user_asset_in_db.as_fields_dict(exclude={'id', }),
    )

    pk = await pg_user_asset_repo.upsert(user_asset_data)

    assert pk is None


@pytest.mark.parametrize(
    ['with_rank', 'updated_at', 'outdated'],
    (
        [
            False,
            datetime.datetime.now(tz=datetime.UTC) -
            datetime.timedelta(minutes=constants.ASSET_PRICE_CONSIDER_STALE_AFTER / 2),
            False,
        ],
        [
            True,
            datetime.datetime.now(tz=datetime.UTC) -
            datetime.timedelta(minutes=constants.ASSET_PRICE_CONSIDER_STALE_AFTER * 2),
            True,
        ]
    )
)
async def test_get_user_asset_detail_positive(
        with_rank,
        updated_at,
        outdated,
        user_asset_in_db,
        pg_user_asset_repo,
        user_asset_operation_in_db,
        asset_ticker_price_factory,
        user_asset_address_in_db,
):
    asset_ticker_price = await asset_ticker_price_factory.create_async(
        name=user_asset_in_db.ticker_id,
        updated_at=updated_at,
    )
    params = GetUserAssetDetailInputParams(
        user_id=user_asset_in_db.user_id,
        ticker_id=user_asset_in_db.ticker_id,
        with_rank=with_rank,
    )
    asset_detail = await pg_user_asset_repo.get_user_asset_detail(params=params)

    assert asset_detail is not None
    assert asset_detail.operations_summary is None
    assert asset_detail.public_key_details is None
    assert asset_detail.user_asset.id == user_asset_in_db.id
    assert asset_detail.user_asset.name == user_asset_in_db.name
    assert asset_detail.user_asset.ticker_id == user_asset_in_db.ticker_id
    assert asset_detail.user_asset.price == asset_ticker_price.price
    assert asset_detail.user_asset.outdated is outdated
    assert asset_detail.user_asset.time_when_price_was_update_in_db is not None
    assert asset_detail.user_asset.popularity_rank is None if not with_rank else 1

    assert len(asset_detail.operations) == 1
    operation = asset_detail.operations[0]
    assert operation.id == user_asset_operation_in_db.id
    assert operation.type == user_asset_operation_in_db.type
    assert operation.quantity == user_asset_operation_in_db.quantity
    assert operation.unit_price == user_asset_operation_in_db.unit_price
    assert operation.summ == user_asset_operation_in_db.summ
    assert operation.time == user_asset_operation_in_db.time
    assert operation.wallet_name == user_asset_address_in_db.wallet_name
    assert operation.public_key == user_asset_address_in_db.public_key
    assert user_asset_address_in_db.user_id == user_asset_in_db.user_id


async def test_get_user_asset_detail_negative(
        pg_user_asset_repo,
):
    params = GetUserAssetDetailInputParams(
        user_id=uuid.uuid7(),
        ticker_id='Random_ticker_name',
        with_rank=False,
    )
    asset_detail = await pg_user_asset_repo.get_user_asset_detail(params=params)

    assert asset_detail is None
