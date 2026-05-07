import pytest
from sqlalchemy.exc import IntegrityError

import constants


async def test_user_asset_address_positive(
        user_asset_address_in_db,
        pg_user_asset_address_repo,
):
    address_from_db = await pg_user_asset_address_repo.get_by_pubkey(user_asset_address_in_db.public_key)
    assert address_from_db.as_fields_dict() == user_asset_address_in_db.as_fields_dict()


async def test_user_asset_address_negative_pub_key_non_unique(
    user_asset_address_in_db,
    user_asset_address_factory,
):
    existing_pub_key = user_asset_address_in_db.public_key
    existing_user_id = user_asset_address_in_db.user_id

    with pytest.raises(IntegrityError) as excinfo:
        await user_asset_address_factory.create_async(public_key=existing_pub_key, user_id=existing_user_id)

    assert excinfo.value.orig.pgcode == constants.PG_UNIQUE_CONSTRAINT_VIOLATION_CODE


async def test_asset_ticker_positive(asset_ticker_in_db, pg_asset_ticker_repo):
    ticker_from_db = await pg_asset_ticker_repo.get_by_name(asset_ticker_in_db.name)
    assert ticker_from_db.as_fields_dict() == asset_ticker_in_db.as_fields_dict()


async def test_asset_ticker_negative_lower(asset_ticker_factory):
    with pytest.raises(IntegrityError) as excinfo:
        await asset_ticker_factory.create_async(name='lower')

    assert excinfo.value.orig.pgcode == constants.PG_CHECK_CONSTRAINT_VIOLATION_CODE


async def test_user_asset_positive(user_asset_in_db, pg_user_asset_repo):
    user_asset_from_db = await pg_user_asset_repo.get_by_id(user_asset_in_db.id)

    assert user_asset_from_db.as_fields_dict() == user_asset_from_db.as_fields_dict()


async def test_user_asset_negative_non_unique(user_asset_in_db, user_asset_factory):
    with pytest.raises(IntegrityError) as excinfo:
        await user_asset_factory.create_async(
            user_id=user_asset_in_db.user_id,
            ticker_id=user_asset_in_db.ticker_id,
        )

    assert excinfo.value.orig.pgcode == constants.PG_UNIQUE_CONSTRAINT_VIOLATION_CODE


async def test_user_asset_operation_positive(user_asset_operation_in_db, pg_user_asset_operation_repo):
    user_asset_operation_from_db = await pg_user_asset_operation_repo.get_by_id(user_asset_operation_in_db.id)
    assert user_asset_operation_from_db.as_fields_dict() == user_asset_operation_in_db.as_fields_dict()


@pytest.mark.parametrize(['quantity', 'unit_price'], [[-1, 1], [1, -1]])
async def test_user_asset_operation_negative_quantity(
        user_asset_operation_factory,
        user_asset_in_db,
        user_asset_address_in_db,
        quantity,
        unit_price,
):
    with pytest.raises(IntegrityError) as excinfo:
        await user_asset_operation_factory.create_async(
            user_asset_id=user_asset_in_db.id,
            address_id=user_asset_address_in_db.id,
            quantity=quantity,
            unit_price=unit_price,
        )

    assert excinfo.value.orig.pgcode == constants.PG_CHECK_CONSTRAINT_VIOLATION_CODE
