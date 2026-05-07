from litestar import Controller, post, put, delete
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory, asset_not_found_error_handler_factory
from api.user_asset_addresses.domain import (
    UserAssetAddressData,
    UserAssetAddressDto,
    UserAssetAddressUpdateData,
    UserAssetAddressUpdateDTOIn,
    UserAssetAddressDeleteData,
    UserAssetAddressDeleteDataDTOIn,
)
from constants import PG_UNIQUE_CONSTRAINT_VIOLATION_CODE
from logic.exceptions import AssetNotFoundError
from logic.usecases.user_asset_address import (
    UserAssetAddressUpdateUseCase,
    UserAssetAddressInsertUseCase,
    UserAssetDeleteUseCase,
)
from user.domain import User


class UserAssetAddressController(Controller):
    path = 'user_asset_address'
    tags = ('user_asset_address', )
    exception_handlers =  {
        IntegrityError: integrity_error_handler_factory(
            'Same public key already exists',
            'Provide alternative public key or leve this one alone.',
            PG_UNIQUE_CONSTRAINT_VIOLATION_CODE,
            'user_asset_address_already_exists.html',
        ),
        AssetNotFoundError: asset_not_found_error_handler_factory(
            'Public key does not exists',
            'Public key can not be updated as it does not exists. You need to create it first',
            'user_asset_address_not_exists.html',
        )
    }

    @post(
        '/',
        dto=UserAssetAddressDto,
    )
    async def create(self, data: DTOData[UserAssetAddressData], kc_user: User) -> UserAssetAddressData:
        user_asset_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetAddressInsertUseCase().execute(user_asset_data)
        return user_asset_data

    @put(
        '/',
        dto=UserAssetAddressUpdateDTOIn,
        return_dto=UserAssetAddressDto,
        responses={
            HTTP_400_BAD_REQUEST: ResponseSpec(
                data_container=ProblemDetailResponse,
                description='Non-unique or non-existing public key',
            )
        }
    )
    async def update(self, data: DTOData[UserAssetAddressUpdateData], kc_user: User) -> UserAssetAddressData:
        user_asset_update_data = data.create_instance(new_data__user_id=kc_user.sub)
        return await UserAssetAddressUpdateUseCase().execute(user_asset_update_data)

    @delete(
        '/',
        dto=UserAssetAddressDeleteDataDTOIn,
        responses={
            HTTP_400_BAD_REQUEST: ResponseSpec(
                data_container=ProblemDetailResponse,
                description='Non-existing public key',
            )
        }
    )
    async def delete(self, data: DTOData[UserAssetAddressDeleteData], kc_user: User) -> None:
        user_asset_delete_data = data.create_instance(user_id=kc_user.sub)
        return await UserAssetDeleteUseCase().execute(data=user_asset_delete_data)


