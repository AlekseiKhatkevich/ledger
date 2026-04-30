from litestar.status_codes import HTTP_201_CREATED

from api.user_assets.crud import UserAssetCrudController


async def test_user_asset_crud_create(asset_ticker_in_db, httpx_test_client):
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
