from litestar import Controller, route, get
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory
from api.pagination import PAGE_SIZE_PARAMETER, UserAssetsPaginator, AdvancedCursorPagination
from api.user_assets.domain import UserAssetData, UserAssetDto, UserAssetAggregatedData
from constants import PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE
from logic.usecases.user_asset import UserAssetUpsertUseCase
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

    # todo ну и всю схему с ценой на сейчас реализовать
    # todo отключить запись трасс в тестах
    # todo caddy opentelemetry, на сам посттгресс и мимио и темпорал
    # todo тесты
    # todo вопрос с тестовым клиентом
    # todo тесты update_if_valid и delete_if_valid
    # todo restict healthceck https://docs.litestar.dev/latest/reference/contrib/opentelemetry.html#litestar.contrib.opentelemetry.OpenTelemetryConfig.exclude_urls_env_key
    @get('/')
    async def get_all_paginated(
            self,
            kc_user: User,
            cursor: str | None = None,
            results_per_page: int = PAGE_SIZE_PARAMETER,
    ) -> AdvancedCursorPagination[str, UserAssetAggregatedData]:
        paginator = UserAssetsPaginator(user_id=kc_user.id)
        return await paginator(cursor=cursor, results_per_page=results_per_page)