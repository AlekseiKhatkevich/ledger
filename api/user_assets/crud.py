import dataclasses
import uuid
from typing import Annotated, TypeVar, Generic, Optional, List

from litestar import Controller, route, get
from litestar.dto import DTOData
from litestar.openapi import ResponseSpec
from litestar.openapi.spec import Example
from litestar.params import Parameter
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from api.common_domain import ProblemDetailResponse
from api.exceptions_handling import integrity_error_handler_factory
from api.user_assets.domain import UserAssetData, UserAssetDto, UserAssetAggregatedPage, UserAssetAggregatedData
from constants import (
    PG_FOREIGN_KEY_CONSTRAINT_VIOLATION_CODE,
    USER_ASSET_LIST_VIEW_DEFAULT_PAGE_SIZE,
    USER_ASSET_LIST_VIEW_MAX_PAGE_SIZE,
)
from logic.usecases.user_asset import UserAssetUpsertUseCase, UserAssetListUseCase
from user.domain import User
from litestar.pagination import AbstractAsyncCursorPaginator, C, T


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



# todo проверить схему
# todo caddy opentelemetry
# todo тесты
    @get('/')
    async def get_all_paginated(
            self,
            kc_user: User,
            cursor: str | None,
            results_per_page: int
    ) -> CursorPagination[str,UserAssetAggregatedData]:
        paginator = UserAssetsPaginator(user_id=kc_user.id)
        return await paginator(cursor=cursor, results_per_page=results_per_page)

T = TypeVar("T")
C = TypeVar("C", int, str, uuid.UUID)

@dataclasses.dataclass
class CursorPagination(Generic[C, T]):
    """Container for data returned using cursor pagination."""

    __slots__ = ("cursor", "items", "next_cursor", "results_per_page", "has_more")

    items: List[T]
    """List of data being sent as part of the response."""
    results_per_page: int
    """Maximal number of items to send."""
    cursor: Optional[C]  # noqa: UP045
    """Unique ID, designating the last identifier in the given data set.
    This value can be used to request the "next" batch of records.
    """
    has_more: bool

class UserAssetsPaginator(AbstractAsyncCursorPaginator[str, UserAssetAggregatedData]):
    def __init__(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id

    async def get_items(self, cursor: C | None, results_per_page: int) -> tuple[list[T], C | None]:
        data = await UserAssetListUseCase().execute(self.user_id, cursor, results_per_page)
        return data.items, data.cursor, data.has_more

    async def __call__(self, cursor: C | None, results_per_page: int) -> CursorPagination[C, T]:
        """Return a paginated result set given an optional cursor (unique ID) and a maximal number of results to return.

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A paginated result set.
        """
        items, new_cursor, has_more = await self.get_items(cursor=cursor, results_per_page=results_per_page)

        return CursorPagination[C, T](
            items=items,
            results_per_page=results_per_page,
            cursor=new_cursor,
            has_more=has_more
        )
