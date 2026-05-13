import decimal

import msgspec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT

from api.user_asset_operations.crud import UserAssetAddressOperationController
from logic.db_models import AssetOperationType


async def test_user_asset_operation_crud_create_purchase(
        user_asset_in_db,
        user_asset_address_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
        user_asset_operation_data_factory,
):
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.post(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_201_CREATED
    response_json = response.json()
    assert response_json['type'] == AssetOperationType.PURCHASE
    assert decimal.Decimal(response_json['quantity']) == data.quantity
    assert decimal.Decimal(response_json['unit_price']) == data.unit_price
    assert response_json['user_asset_id'] == user_asset_in_db.id
    assert response_json['address_id'] == user_asset_address_in_db.id
    assert response_json['id'] is not None

    instance_from_db = await pg_user_asset_operation_repo.get_by_id(response_json['id'])
    assert instance_from_db is not None
    assert instance_from_db.type.value == AssetOperationType.PURCHASE
    assert instance_from_db.quantity == data.quantity
    assert instance_from_db.unit_price == data.unit_price


async def test_user_asset_operation_crud_create_negative_user_asset_not_found(
        user_asset_address_in_db,
        httpx_test_client,
        user_asset_operation_data_factory,
        pg_user_asset_operation_repo,
):
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_asset_id=999999,
        address_id=user_asset_address_in_db.id,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.post(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'User asset does not not exists'

    instance_from_db = await pg_user_asset_operation_repo.get_by_field_names(
        user_asset_id=999999,
        address_id=user_asset_address_in_db.id,
    )
    assert instance_from_db is None


async def test_user_asset_operation_crud_create_negative_address_not_found(
        user_asset_in_db,
        httpx_test_client,
        user_asset_operation_data_factory,
        pg_user_asset_operation_repo,
):
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_asset_id=user_asset_in_db.id,
        address_id=999999,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.post(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'Public key does not exists'

    instance_from_db = await pg_user_asset_operation_repo.get_by_field_names(
        user_asset_id=user_asset_in_db.id,
        address_id=999999,
    )
    assert instance_from_db is None


async def test_user_asset_operation_crud_create_sell(
        purchase_operation_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
        user_asset_operation_data_factory,
):
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.SELL,
        user_asset_id=purchase_operation_in_db.user_asset_id,
        address_id=purchase_operation_in_db.address_id,
        quantity=purchase_operation_in_db.quantity,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.post(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_201_CREATED
    response_json = response.json()
    assert response_json['type'] == AssetOperationType.SELL
    assert response_json['id'] is not None

    instance_from_db = await pg_user_asset_operation_repo.get_by_id(response_json['id'])
    assert instance_from_db is not None
    assert instance_from_db.type.value == AssetOperationType.SELL


async def test_user_asset_operation_crud_create_negative_not_enough_balance(
        user_asset_in_db,
        user_asset_address_in_db,
        httpx_test_client,
        user_asset_operation_data_factory,
        pg_user_asset_operation_repo,
):
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.SELL,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.post(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'Balance is to small'

    instance_from_db = await pg_user_asset_operation_repo.get_by_field_names(
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
        type=AssetOperationType.SELL,
    )
    assert instance_from_db is None


async def test_user_asset_operation_crud_update(
        purchase_operation_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
        user_asset_operation_data_factory,
):
    new_data = user_asset_operation_data_factory.build(
        id=purchase_operation_in_db.id,
        type=purchase_operation_in_db.type,
        user_asset_id=purchase_operation_in_db.user_asset_id,
        address_id=purchase_operation_in_db.address_id,
    )
    input_data = msgspec.to_builtins(new_data)

    response = await httpx_test_client.put(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_200_OK
    response_json = response.json()
    assert response_json['id'] == purchase_operation_in_db.id
    assert decimal.Decimal(response_json['quantity']) == new_data.quantity
    assert decimal.Decimal(response_json['unit_price']) == new_data.unit_price

    instance_from_db = await pg_user_asset_operation_repo.get_by_id(purchase_operation_in_db.id)
    assert instance_from_db is not None
    assert instance_from_db.quantity == new_data.quantity
    assert instance_from_db.unit_price == new_data.unit_price


async def test_user_asset_operation_crud_update_negative_not_found(
        user_asset_in_db,
        user_asset_address_in_db,
        httpx_test_client,
        user_asset_operation_data_factory,
):
    data = user_asset_operation_data_factory.build(
        id=999999,
        type=AssetOperationType.PURCHASE,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.put(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'User asset operation does not exists'


async def test_user_asset_operation_crud_update_negative_not_enough_balance(
        purchase_operation_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
        user_asset_operation_data_factory,
):
    data = user_asset_operation_data_factory.build(
        id=purchase_operation_in_db.id,
        type=AssetOperationType.SELL,
        user_asset_id=purchase_operation_in_db.user_asset_id,
        address_id=purchase_operation_in_db.address_id,
        quantity=purchase_operation_in_db.quantity,
    )
    input_data = msgspec.to_builtins(data)

    response = await httpx_test_client.put(
        UserAssetAddressOperationController.path,
        json=input_data,
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'Balance is to small'

    instance_from_db = await pg_user_asset_operation_repo.get_by_id(purchase_operation_in_db.id)
    assert instance_from_db is not None
    assert instance_from_db.type.value == AssetOperationType.PURCHASE


async def test_user_asset_operation_crud_delete(
        purchase_operation_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
):
    response = await httpx_test_client.delete(
        f'{UserAssetAddressOperationController.path}/{purchase_operation_in_db.id}',
    )

    assert response.status_code == HTTP_204_NO_CONTENT

    instance_from_db = await pg_user_asset_operation_repo.get_by_id(purchase_operation_in_db.id)
    assert instance_from_db is None


async def test_user_asset_operation_crud_delete_negative_not_found(
        httpx_test_client,
):
    response = await httpx_test_client.delete(
        f'{UserAssetAddressOperationController.path}/999999',
    )

    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json()['title'] == 'User asset operation does not exists'
