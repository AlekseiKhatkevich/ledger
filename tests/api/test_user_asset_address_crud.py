import msgspec
from litestar.status_codes import HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from api.user_asset_addresses.crud import UserAssetAddressController


async def test_create_positive(
        httpx_test_client,
        user_asset_address_data_factory,
        jwt_user,
        pg_user_asset_address_repo
):

    data = user_asset_address_data_factory.build()
    input_data = {'public_key': data.public_key, 'wallet_name': data.wallet_name}

    response = await httpx_test_client.post(
        UserAssetAddressController.path,
        json=input_data,
    )
    assert response.status_code == HTTP_201_CREATED
    assert response.json() == input_data

    instance_from_db = await pg_user_asset_address_repo.get_by_field_names(
        public_key=data.public_key,
        wallet_name=data.wallet_name,
        user_id=jwt_user.id,
    )
    assert instance_from_db is not None


async def test_update_positive(
        httpx_test_client,
        jwt_user,
        pg_user_asset_address_repo,
        user_asset_address_in_db,
        user_asset_address_update_data_factory,
):
    random_data = user_asset_address_update_data_factory.build()
    input_data = {
        'public_key': user_asset_address_in_db.public_key,
        'new_data': {
            'public_key': random_data.new_data.public_key,
            'wallet_name':random_data.new_data.wallet_name,
        }
    }

    response = await httpx_test_client.put(
        UserAssetAddressController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_200_OK
    instance_from_db = await pg_user_asset_address_repo.get_by_field_names(
        public_key=input_data['new_data']['public_key'],
        wallet_name=input_data['new_data']['wallet_name'],
        user_id=jwt_user.id,
    )
    assert instance_from_db is not None


async def test_update_negative_uniqueness_violation(
        httpx_test_client,
        jwt_user,
        user_asset_address_in_db,
        user_asset_address_factory,
):
    another_instance = await user_asset_address_factory.create_async(user_id=jwt_user.sub)

    input_data = {
        'public_key': user_asset_address_in_db.public_key,
        'new_data': {
            'public_key': another_instance.public_key,
            'wallet_name': ['test',],
        }
    }

    response = await httpx_test_client.put(
        UserAssetAddressController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == "Same public key already exists"


async def test_update_negative_not_found(
        httpx_test_client,
        user_asset_address_update_data_factory,
):
    input_data = msgspec.to_builtins(user_asset_address_update_data_factory.build())

    response = await httpx_test_client.put(
        UserAssetAddressController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'Public key does not exists'


async def test_delete_positive(
        httpx_test_client,
        user_asset_address_in_db,
        pg_user_asset_address_repo,
        jwt_user,
):
    input_data = {
        'public_key': user_asset_address_in_db.public_key,
    }

    response = await httpx_test_client.post(
        UserAssetAddressController.path + '/delete',
        json=input_data,
    )

    assert response.status_code == HTTP_204_NO_CONTENT

    instance_from_db = await pg_user_asset_address_repo.get_by_field_names(
        public_key=input_data['public_key'],
        user_id=jwt_user.id,
    )
    assert instance_from_db is None


async def test_delete_negative_no_instance_in_db(
        httpx_test_client,
        jwt_user,
        user_asset_address_delete_data_factory,
):
    input_data = msgspec.to_builtins(user_asset_address_delete_data_factory.build())

    response = await httpx_test_client.post(
        UserAssetAddressController.path + '/delete',
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'Public key does not exists'
