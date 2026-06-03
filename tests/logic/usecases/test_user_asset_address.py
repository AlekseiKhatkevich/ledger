import pytest

from logic.exceptions import UserAssetAddressNotFoundError
from logic.usecases.user_asset_address import UserAssetAddressUpdateUseCase, UserAssetDeleteUseCase


async def test_user_asset_address_update_usecase_positive(
    user_asset_address_update_data_factory,
    user_asset_address_in_db
):
    data = user_asset_address_update_data_factory.build(
        public_key=user_asset_address_in_db.public_key,
        new_data={'user_id': user_asset_address_in_db.user_id}
    )

    instance_from_db = await UserAssetAddressUpdateUseCase().execute(data)
    assert instance_from_db == data.new_data


async def test_user_asset_address_update_usecase_negative_not_found(
    user_asset_address_update_data_factory,
):
    with pytest.raises(UserAssetAddressNotFoundError):
        await UserAssetAddressUpdateUseCase().execute(user_asset_address_update_data_factory.build())


async def test_user_asset_address_delete_usecase_positive(
    user_asset_address_delete_data_factory,
    user_asset_address_in_db
):
    data = user_asset_address_delete_data_factory.build(
        user_id=user_asset_address_in_db.user_id,
        public_key=user_asset_address_in_db.public_key,
    )

    resp = await UserAssetDeleteUseCase().execute(data)

    assert resp is None


async def test_user_asset_address_delete_usecase_negative_not_found(
    user_asset_address_delete_data_factory,
):
    with pytest.raises(UserAssetAddressNotFoundError):
        await UserAssetDeleteUseCase().execute(user_asset_address_delete_data_factory.build())
