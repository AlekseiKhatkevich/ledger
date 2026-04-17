import pytest
from sqlalchemy.exc import IntegrityError


async def test_user_asset_address_positive(
        user_asset_address_in_db,
        pg_user_asset_repo,
):
    address_from_db = await pg_user_asset_repo.get_by_pubkey(user_asset_address_in_db.public_key)
    assert address_from_db.as_fields_dict() == user_asset_address_in_db.as_fields_dict()


async def test_user_asset_address_negative_pub_key_non_unique(
    user_asset_address_in_db,
    user_asset_address_factory,
):
    existing_pub_key = user_asset_address_in_db.public_key

    with pytest.raises(IntegrityError) as excinfo:
        await user_asset_address_factory.create_async(public_key=existing_pub_key)

    assert excinfo.value.orig.pgcode == '23505'


async def test_asset_ticker_positive(asset_ticker_in_db, pg_asset_ticker_repo):
    ticker_from_db = await pg_asset_ticker_repo.get_by_name(asset_ticker_in_db.name)
    assert ticker_from_db.as_fields_dict() == asset_ticker_in_db.as_fields_dict()

    # todo negetive one