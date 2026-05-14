import dataclasses
import uuid
from abc import ABC, abstractmethod
from typing import Generic, Optional, List, TypeVar

from litestar.exceptions import ValidationException

from api.user_assets.domain import UserAssetAggregatedData
from constants.api import (
    LIST_VIEW_DEFAULT_PAGE_SIZE,
    LIST_VIEW_MAX_PAGE_SIZE,
)
from logic.usecases.user_asset import UserAssetListUseCase

C = TypeVar("C", int, str, uuid.UUID)
T = TypeVar("T")


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
    """Whether there are more results available."""


class AdvancedCursorPaginator(ABC, Generic[C, T]):
    """Base cursor paginator that adds ``has_more`` support.

    Subclasses must implement :meth:`get_items` returning
    ``(items, next_cursor, has_more)``.
    """

    default_page_size: int = 20
    """Default number of results per page."""
    max_page_size: int = 100
    """Maximum allowed number of results per page."""

    @abstractmethod
    async def get_items(
        self,
        cursor: C | None,
        results_per_page: int,
    ) -> tuple[list[T], C | None, bool]:
        """Return a page of items following the given cursor.

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which
                results should be given.
            results_per_page: A maximal number of results to return.

        Returns:
            A tuple containing the result set, a new cursor that marks the
            last record retrieved, and a boolean indicating whether there
            are more results.
        """
        raise NotImplementedError

    async def __call__(
        self,
        cursor: C | None = None,
        results_per_page: int | None = None,
    ) -> CursorPagination[C, T]:
        """Return a paginated result set given an optional cursor (unique ID)
        and a maximal number of results to return.

        Args:
            cursor: A unique identifier that acts as the 'cursor' after which
                results should be given.
            results_per_page: A maximal number of results to return.
                If not provided, defaults to :attr:`default_page_size`.

        Returns:
            A paginated result set.
        """
        if results_per_page is None:
            results_per_page = self.default_page_size
        elif results_per_page < 1:
            raise ValidationException(
                detail=f"results_per_page must be >= 1, got {results_per_page}",
            )
        elif results_per_page > self.max_page_size:
            raise ValidationException(
                detail=f"results_per_page must be <= {self.max_page_size}, got {results_per_page}",
            )

        items, new_cursor, has_more = await self.get_items(cursor=cursor, results_per_page=results_per_page)

        return CursorPagination[C, T](
            items=items,
            results_per_page=results_per_page,
            cursor=new_cursor,
            has_more=has_more,
        )


class UserAssetsPaginator(AdvancedCursorPaginator[str, UserAssetAggregatedData]):
    """Paginator for aggregated user asset data."""

    default_page_size = LIST_VIEW_DEFAULT_PAGE_SIZE
    max_page_size = LIST_VIEW_MAX_PAGE_SIZE

    def __init__(self, user_id: uuid.UUID) -> None:
        self.user_id = user_id

    async def get_items(
        self,
        cursor: str | None,
        results_per_page: int,
    ) -> tuple[list[UserAssetAggregatedData], str | None, bool]:
        data = await UserAssetListUseCase().execute(self.user_id, cursor, results_per_page)
        return data.items, data.cursor, data.has_more