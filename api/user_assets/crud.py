from typing import Callable

from litestar import Controller, route, Request, Response, MediaType
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import CommonErrorResponse
from api.user_assets.domain import UserAssetData, UserAssetDto
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION
from logic.usecases.user_asset_upsert import UserAssetUpsertUseCase
from user.domain import User


def integrity_error_handler_factory(
        description: str,
        pg_error_code: str,
) -> Callable[[Request, IntegrityError], Response]:
    def _handler(_: Request, exc: IntegrityError) -> Response:
            if exc.orig.pgcode == pg_error_code:
                return Response(
                    media_type=MediaType.JSON,
                    content={'detail': description, 'status_code': HTTP_400_BAD_REQUEST},
                    status_code=HTTP_400_BAD_REQUEST,
                )
            else:
                raise exc
    return _handler


class UserAssetCrudController(Controller):
    path = '/user_asset'
    tags = ('user_asset', )
    exception_handlers = {
        IntegrityError: integrity_error_handler_factory(
            'Ticker is incorrect or unknown',
            PG_FOREIGN_KEY_CONSTRAINT_VIOLATION,
        ),
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
