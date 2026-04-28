import sqlalchemy
from litestar import Controller, route, Request, Response, MediaType
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import CommonErrorResponse
from api.user_assets.domain import UserAssetData, UserAssetDto
from logic.usecases.user_asset_upsert import UserAssetUpsertUseCase
from user.domain import User
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION


def unknown_ticker_exception_handler(_: Request, exc: IntegrityError) -> Response:
        if exc.orig.pgcode == PG_FOREIGN_KEY_CONSTRAINT_VIOLATION:
            return Response(
                media_type=MediaType.JSON,
                content={'detail': 'Ticker is unknown', 'status_code': HTTP_400_BAD_REQUEST},
                status_code=HTTP_400_BAD_REQUEST,
            )
        else:
            raise exc

class UserAssetCrudController(Controller):
    path = '/user_asset'
    tags = ('user_asset', )
    exception_handlers = {
        IntegrityError: unknown_ticker_exception_handler,
    }


    @route(
        '/',
        dto=UserAssetDto,
        http_method=["POST", "PUT", "PATCH"],
        responses={
            HTTP_400_BAD_REQUEST: ResponseSpec(
                data_container=CommonErrorResponse,
                description='Wrong or unknown ticker',
            )
        }
    )
    async def create_or_update(self, data: DTOData[UserAssetData], kc_user: User) -> UserAssetData:
        user_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetUpsertUseCase().execute(user_data)
        return user_data
