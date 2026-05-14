from typing import Annotated

from litestar import Controller, route, get
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Parameter
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory
from api.user_assets.domain import UserAssetData, UserAssetDto, UserAssetAggregatedPage
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE, USER_ASSET_LIST_VIEW_DEFAULT_PAGE_SIZE, \
    USER_ASSET_LIST_VIEW_MAX_PAGE_SIZE
from logic.usecases.user_asset import UserAssetUpsertUseCase, UserAssetListUseCase
from user.domain import User


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
                data_container=ProblemDetailResponse,
                description='Wrong or unknown ticker',
            )
        }
    )
    async def create_or_update(self, data: DTOData[UserAssetData], kc_user: User) -> UserAssetData:
        user_data = data.create_instance(user_id=kc_user.sub)
        await UserAssetUpsertUseCase().execute(user_data)
        return user_data

# todo built-in LS paginator
# todo проверить схему
# todo caddy opentelemetry
# todo тесты
    @get('/')
    async def get_all_paginated(
            self,
            kc_user: User,
            last_ticker_id: Annotated[
                str | None,
                Parameter(
                    description='Last ticker from rev. page response',
                    examples=[Example(value='XRP', description='Any valid token name')],
                    max_length=30,
                )
            ] = None,
            page_size: Annotated[
                int,
                Parameter(
                    description='Pagination page size',
                    ge=1,
                    le=USER_ASSET_LIST_VIEW_MAX_PAGE_SIZE,
                ),
            ] = USER_ASSET_LIST_VIEW_DEFAULT_PAGE_SIZE,
    ) -> UserAssetAggregatedPage:
        return await UserAssetListUseCase().execute(kc_user.sub, last_ticker_id, page_size)
