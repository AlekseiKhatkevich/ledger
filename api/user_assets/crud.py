import asyncio
import datetime
from collections.abc import AsyncGenerator

import msgspec.json
from litestar import Controller, route, get
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.params import FromPath, FromQuery
from litestar.response.sse import ServerSentEvent
from litestar.status_codes import HTTP_400_BAD_REQUEST
from litestar.types import SSEData
from sqlalchemy.exc import IntegrityError

import constants
from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory, base_error_handler_factory
from api.pagination import PAGE_SIZE_PARAMETER, UserAssetsPaginator, AdvancedCursorPagination
from api.user_asset_operations.domain import UserAssetOperationsFilter
from api.user_assets.domain import (
    UserAssetData,
    UserAssetDto,
    UserAssetAggregatedData,
    GetUserAssetDetailInputParams, UserAssetDetailCombinedOut,
)
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE
from logic.db_models import AssetOperationType
from logic.exceptions import UserAssetNotFoundError
from logic.usecases.user_asset import UserAssetUpsertUseCase, UserAssetDetailUseCase
from user.domain import User


# noinspection PyShadowingBuiltins
def fill_filter(
    time__gte: FromQuery[datetime.datetime | None] = None,
    time__lte: FromQuery[datetime.datetime | None] = None,
    id: FromQuery[list[int] | None] = None,
    type: FromQuery[AssetOperationType | None] = None,
    address_id: FromQuery[list[int] | None] = None
) -> UserAssetOperationsFilter:
    return UserAssetOperationsFilter(
        time__gte=time__gte,
        time__lte=time__lte,
        id=id,
        type=type,
        address_id=address_id,
    )


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
        http_method=['POST', 'PUT',],
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
            cursor: FromQuery[str | None] = None,
            results_per_page: int = PAGE_SIZE_PARAMETER,
    ) -> AdvancedCursorPagination[str, UserAssetAggregatedData]:
        paginator = UserAssetsPaginator(user_id=kc_user.id)
        return await paginator(cursor=cursor, results_per_page=results_per_page)

    @get('/{ticker_id: str}', dependencies={'op_filter': Provide(fill_filter)})
    async def get_exact_user_asset(
            self,
            kc_user: User,
            op_filter: UserAssetOperationsFilter,
            ticker_id: FromPath[str],
            with_rank: FromQuery[bool] = False,
    ) -> ServerSentEvent:
        params = GetUserAssetDetailInputParams(
            user_id=kc_user.id,
            ticker_id=ticker_id,
            with_rank=with_rank,
        )

        def _get_response_message(data) -> dict[str, str | bytes]:
            if isinstance(data, UserAssetDetailCombinedOut):
                event = 'initial'
            else:
                event = 'price_update'
            return {
                'event': event,
                'data': msgspec.json.encode(data)
            }

        async def _user_asset_stream() -> AsyncGenerator[SSEData, None]:
            """SSE generator for user asset detail.

            First event ('initial') sends full asset data.
            Subsequent events ('price_update') will be emitted when
            the price-update mechanism is implemented.
            """
            usecase = UserAssetDetailUseCase(constants.ASSET_PRICE_UPDATE_INTERVAL)
            await usecase.execute(params)

            try:
                while True:
                    try:
                        new_data = await asyncio.wait_for(
                            usecase.result_queue.get(),
                            constants.SSE_KEEPALIVE_TIMEOUT,
                        )
                    except TimeoutError:
                        yield {'comment': 'ping'}
                    else:
                        usecase.result_queue.task_done()
                        yield _get_response_message(new_data)
            finally:
                usecase.final_event.set()

        return ServerSentEvent(
            content=_user_asset_stream(),
            retry_duration=3000,
        )