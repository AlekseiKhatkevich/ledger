import datetime

import constants


async def test_get_prices_fresh(
        pg_asset_ticker_price_repo,
        asset_ticker_price_in_db,
):
    prices_from_db = await pg_asset_ticker_price_repo.get_prices(
        {asset_ticker_price_in_db.name, }
    )

    assert len(prices_from_db) == 1
    assert prices_from_db[0].name == asset_ticker_price_in_db.name
    assert prices_from_db[0].outdated is not None
    assert not prices_from_db[0].outdated


async def test_get_prices_stale(
        asset_ticker_price_factory,
        pg_asset_ticker_price_repo,
        asset_ticker_in_db,
):
    price_in_db = await asset_ticker_price_factory.create_async(
        name=asset_ticker_in_db.name,
        updated_at=datetime.datetime.now(tz=datetime.UTC) - \
                 datetime.timedelta(minutes=constants.ASSET_PRICE_CONSIDER_STALE_AFTER * 2)
    )

    prices_from_db = await pg_asset_ticker_price_repo.get_prices(
        {price_in_db.name, }
    )

    assert len(prices_from_db) == 1
    assert prices_from_db[0].name == price_in_db.name
    assert prices_from_db[0].outdated


async def test_get_prices_negative(
        pg_asset_ticker_price_repo,
        asset_ticker_price_in_db,
):
    prices_from_db = await pg_asset_ticker_price_repo.get_prices(
        {'Random_ticker_name', }
    )

    assert not prices_from_db
