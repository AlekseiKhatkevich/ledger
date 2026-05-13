import decimal

import msgspec
from litestar.status_codes import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from api.user_asset_operations.crud import UserAssetAddressOperationController
from logic.db_models import AssetOperationType


async def test_user_asset_operation_crud_create_purchase(
        user_asset_in_db,
        user_asset_address_in_db,
        httpx_test_client,
        pg_user_asset_operation_repo,
        user_asset_operation_data_factory,
):
    # Создаем данные операции через фабрику, подставляя реальные ID ассета и адреса
    data = user_asset_operation_data_factory.build(
        type=AssetOperationType.PURCHASE,
        user_asset_id=user_asset_in_db.id,
        address_id=user_asset_address_in_db.id,
    )
    # Преобразуем msgspec.Struct в dict для отправки JSON;
    # user_id и id исключаются, так как DTOConfig их не ожидает на входе
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
    # Пытаемся создать операцию с несуществующим user_asset_id
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

    # Проверяем, что в БД не создалась запись
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
    # Пытаемся создать операцию с несуществующим address_id
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

    # Проверяем, что в БД не создалась запись
    instance_from_db = await pg_user_asset_operation_repo.get_by_field_names(
        user_asset_id=user_asset_in_db.id,
        address_id=999999,
    )
    assert instance_from_db is None
