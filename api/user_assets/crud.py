from typing import Callable, NoReturn

from litestar import Controller, route, Request
from litestar.datastructures import URL
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.plugins.problem_details import ProblemDetailsException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import CommonErrorResponse
from api.user_assets.domain import UserAssetData, UserAssetDto
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE
from logic.usecases.user_asset_upsert import UserAssetUpsertUseCase
from user.domain import User


def integrity_error_handler_factory(
        title: str,
        detail: str,
        pg_error_code: str,
        error_html: str,
) -> Callable[[Request, IntegrityError], NoReturn]:
    def _handler(request: Request, exc: IntegrityError) -> NoReturn:
            if exc.orig.pgcode == pg_error_code:
                url = URL.from_components(
                    'https',
                    request.url.netloc,
                    request.url.path,
                    request.url.fragment,
                    request.url.query,
                )
                raise ProblemDetailsException(
                    type_=f"https://{request.url.netloc}/error-descriptions/{error_html}",
                    title=title,
                    detail=detail,
                    instance=str(url),
                    extra={},
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
            'Provide correct ticker. All available tickers are on Coingecko.',
            PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE,
            'wrong_ticker.html',
        ),
    }

    @route(
        '/',
        dto=UserAssetDto,
        http_method=["POST", "PUT",],
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
