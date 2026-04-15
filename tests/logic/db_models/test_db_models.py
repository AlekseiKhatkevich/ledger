

async def test_user_asset_address_positive(
        # user_asset_address_factory,
        user_asset_address_in_db,
        pg_user_asset_repo,
        monkeypatch
):
    monkeypatch.setenv('PGDATABASE', 'ledger-db-test')
    address_from_db = await pg_user_asset_repo.get_by_pubkey(user_asset_address_in_db.public_key)
    assert address_from_db.as_fields_dict() == user_asset_address_in_db.as_fields_dict()