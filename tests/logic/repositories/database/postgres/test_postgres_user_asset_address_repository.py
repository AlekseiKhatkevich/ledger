

async def test_insert_positive(user_asset_address_data_factory, pg_user_asset_address_repo):
    data = user_asset_address_data_factory.build()

    instance_id = await pg_user_asset_address_repo.insert(data)

    assert instance_id is not None
    instance_from_db = await pg_user_asset_address_repo.get_by_id(instance_id)
    assert instance_from_db is not None
    assert instance_from_db.to_msgspec(type(data)) == data


async def test_insert_negative_same_pkey_and_user_exists_already(
        user_asset_address_data_factory,
        pg_user_asset_address_repo,
        user_asset_address_in_db,
):
    data = user_asset_address_data_factory.build(
        user_id=user_asset_address_in_db.user_id,
        public_key=user_asset_address_in_db.public_key,
    )

    instance_id = await pg_user_asset_address_repo.insert(data)

    assert instance_id is None


async def test_update_positive(
        user_asset_address_in_db,
        user_asset_address_update_data_factory,
        pg_user_asset_address_repo,
):
    data = user_asset_address_update_data_factory.build(
        public_key=user_asset_address_in_db.public_key,
        new_data={'user_id': user_asset_address_in_db.user_id}
    )

    instance_from_db = await pg_user_asset_address_repo.update(data)

    assert instance_from_db is not None
    assert instance_from_db.to_msgspec(type(data.new_data)) == data.new_data


async def test_update_negative_pub_key_does_not_exists(
        user_asset_address_update_data_factory,
        pg_user_asset_address_repo,
):
    data = user_asset_address_update_data_factory.build()

    instance_from_db = await pg_user_asset_address_repo.update(data)

    assert instance_from_db is  None


async def test_delete_positive(
    pg_user_asset_address_repo,
    user_asset_address_in_db,
    user_asset_address_delete_data_factory,
):
    data = user_asset_address_delete_data_factory.build(
        user_id=user_asset_address_in_db.user_id,
        public_key=user_asset_address_in_db.public_key,
    )

    instance_id = await pg_user_asset_address_repo.delete(data)

    assert instance_id is not None
    instance_from_db = await pg_user_asset_address_repo.get_by_id(instance_id)
    assert instance_from_db is  None


async def test_delete_negative_asset_does_not_exists(
    pg_user_asset_address_repo,
    user_asset_address_delete_data_factory,
):
    data = user_asset_address_delete_data_factory.build()

    instance_id = await pg_user_asset_address_repo.delete(data)

    assert instance_id is None
