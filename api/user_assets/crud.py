import json
from dataclasses import asdict

import anyio
from collections.abc import AsyncGenerator

import msgspec.json
from litestar import Controller, route, get
from litestar.background_tasks import BackgroundTask
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.response.sse import ServerSentEvent
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError
from litestar.params import FromPath, FromQuery
from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory, base_error_handler_factory
from api.pagination import PAGE_SIZE_PARAMETER, UserAssetsPaginator, AdvancedCursorPagination
from api.user_assets.domain import (
    UserAssetData,
    UserAssetDto,
    UserAssetAggregatedData,
    GetUserAssetDetailInputParams,
)
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE
from logic.exceptions import UserAssetNotFoundError
from logic.usecases.user_asset import UserAssetUpsertUseCase, UserAssetDetailUseCase
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
        UserAssetNotFoundError: base_error_handler_factory(
            'User asset does not not exists',
            'User asset with this name does not exists for this user',
            'user_asset_with_exact_name_not_exists.html',
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

    @get('/')
    async def get_all_paginated(
            self,
            kc_user: User,
            cursor: str | None = None,
            results_per_page: int = PAGE_SIZE_PARAMETER,
    ) -> AdvancedCursorPagination[str, UserAssetAggregatedData]:
        paginator = UserAssetsPaginator(user_id=kc_user.id)
        return await paginator(cursor=cursor, results_per_page=results_per_page)


    @get('/{ticker_id: str}')
    async def get_exact_user_asset(
            self,
            kc_user: User,
            ticker_id: FromPath[str],
            with_rank: FromQuery[bool] = False,
    ) -> ServerSentEvent:
        params = GetUserAssetDetailInputParams(
            user_id=kc_user.id,
            ticker_id=ticker_id,
            with_rank=with_rank,
        )

        async def _user_asset_stream() -> AsyncGenerator[dict, None]:
            """SSE generator for user asset detail.

            First event ('initial') sends full asset data.
            Subsequent events ('price_update') will be emitted when
            the price-update mechanism is implemented.
            """
            usecase = UserAssetDetailUseCase()

            initial_data = await usecase.execute(params)
            yield {
                'event': 'initial',
                'data': msgspec.json.encode(initial_data)
            }
            update_prices_result = await usecase.get_price_after_update_in_temporal()
            if update_prices_result is not None:
                yield {
                    'event': 'price_update',
                    'data': msgspec.json.encode(update_prices_result)
                }
            while True:
                try:
                    await anyio.sleep(55)
                    yield {'comment': 'ping'}
                except BaseException:
                    break

        return ServerSentEvent(
            content=_user_asset_stream(),
            retry_duration=3000,
            # background=BackgroundTask(print, ('FINISH NAH', ))
        )
