from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from api.user_assets.crud import UserAssetCrudController


async def test_user_asset_crud_create(asset_ticker_in_db, httpx_test_client, pg_user_asset_repo):
    data = {
        'name': 'test_name',
        'ticker_id': asset_ticker_in_db.name,
    }

    response = await httpx_test_client.post(
                UserAssetCrudController.path ,
                json=data,
            )

    assert response.status_code == HTTP_201_CREATED
    assert response.json() == data

    instance_from_db = await pg_user_asset_repo.get_by_field_names(
        name='test_name',
        ticker_id= asset_ticker_in_db.name,
    )
    assert instance_from_db is not None
    assert instance_from_db.user_id is not None


async def test_user_asset_crud_update(user_asset_in_db, httpx_test_client, pg_user_asset_repo):
    data = {
        'name': 'new_test_name',
        'ticker_id': user_asset_in_db.ticker_id,
    }
    response = await httpx_test_client.post(
        UserAssetCrudController.path,
        json=data,
    )

    assert response.status_code == HTTP_201_CREATED

    instance_from_db = await pg_user_asset_repo.get_by_field_names(
        name='new_test_name',
        ticker_id=user_asset_in_db.ticker_id,
    )
    assert instance_from_db is not None
    assert instance_from_db.user_id == user_asset_in_db.user_id


async def test_user_asset_crud_negative_no_ticker(httpx_test_client):
    data = {
        'name': 'test_name',
        'ticker_id': 'NE',
    }
    response = await httpx_test_client.post(
        UserAssetCrudController.path,
        json=data,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = response.json()
    assert response_data['type'] == 'https://testserver/error-descriptions/wrong_ticker.html'
    assert response_data['title'] == 'Ticker is incorrect or unknown'
    assert response_data['detail'] == 'Provide correct ticker. All available tickers are on Coingecko.'
    assert response_data['instance'] == f'https://testserver{UserAssetCrudController.path}'
