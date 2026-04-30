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
