"""
Tests for the generic pagination machinery in api/pagination.py.

These tests verify the behaviour of ``AdvancedCursorPaginator``,
``AdvancedCursorPagination`` and ``PAGE_SIZE_PARAMETER`` in isolation,
using a mock implementation that replaces the abstract ``get_items``.
"""

import pytest
from litestar.params import Parameter

from api.pagination import (
    AdvancedCursorPagination,
    AdvancedCursorPaginator,
    PAGE_SIZE_PARAMETER,
)
from constants.api import LIST_VIEW_DEFAULT_PAGE_SIZE, LIST_VIEW_MAX_PAGE_SIZE


# ---------------------------------------------------------------------------
# Mock paginator used throughout the test suite
# ---------------------------------------------------------------------------

class _MockPaginator(AdvancedCursorPaginator[int, str]):
    """
    Paginator backed by a fixed list passed at construction time.

    Each call to ``get_items`` slices the internal data list by the
    cursor position and returns up to ``results_per_page`` items.
    The cursor is the integer index of the last returned element.
    """

    def __init__(self, data: list[str], *, default_page_size: int | None = None) -> None:
        self._data = data
        if default_page_size is not None:
            self.default_page_size = default_page_size

    async def get_items(
        self,
        cursor: int | None,
        results_per_page: int,
    ) -> tuple[list[str], int | None, bool]:
        # cursor is the index of the last item on the previous page;
        # the next page starts at cursor + 1 (or 0 for the first page).
        start = 0 if cursor is None else cursor + 1
        page = self._data[start: start + results_per_page]

        if not page:
            return [], None, False

        new_cursor = start + len(page) - 1
        has_more = new_cursor < len(self._data) - 1
        return page, new_cursor, has_more


# ---------------------------------------------------------------------------
# Tests for ``AdvancedCursorPagination`` dataclass
# ---------------------------------------------------------------------------

class TestAdvancedCursorPagination:
    """Structural tests for the dataclass that holds paginated results."""

    def test_fields(self) -> None:
        """Verify the dataclass has the expected fields and types."""
        instance = AdvancedCursorPagination(
            items=["a", "b"],
            results_per_page=20,
            cursor="abc",
            has_more=True,
        )
        assert instance.items == ["a", "b"]
        assert instance.results_per_page == 20
        assert instance.cursor == "abc"
        assert instance.has_more is True

    def test_cursor_can_be_none(self) -> None:
        """The cursor field is typed as optional and may be ``None``."""
        instance = AdvancedCursorPagination(
            items=[],
            results_per_page=20,
            cursor=None,
            has_more=False,
        )
        assert instance.cursor is None

    def test_items_can_be_empty(self) -> None:
        """An empty result set must be representable."""
        instance = AdvancedCursorPagination(
            items=[],
            results_per_page=20,
            cursor=None,
            has_more=False,
        )
        assert instance.items == []


# ---------------------------------------------------------------------------
# Tests for ``PAGE_SIZE_PARAMETER`` (Litestar Parameter descriptor)
# ---------------------------------------------------------------------------

class TestPageSizeParameter:
    """Validates the constraint-driven page-size parameter."""

    def test_default_value(self) -> None:
        assert PAGE_SIZE_PARAMETER.default == LIST_VIEW_DEFAULT_PAGE_SIZE

    def test_minimum(self) -> None:
        """ge=1 – minimum acceptable value."""
        assert PAGE_SIZE_PARAMETER.ge == 1

    def test_maximum(self) -> None:
        """le=100 – maximum acceptable value."""
        assert PAGE_SIZE_PARAMETER.le == LIST_VIEW_MAX_PAGE_SIZE


# ---------------------------------------------------------------------------
# Tests for ``AdvancedCursorPaginator`` generic machinery
# ---------------------------------------------------------------------------

class TestAdvancedCursorPaginator:
    """Behavioural tests for the abstract paginator base."""

    # ── first page ─────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_first_page_default_page_size(self) -> None:
        """
        When called without arguments the paginator fetches the first page
        using ``default_page_size`` as the page size.
        """
        data = [str(i) for i in range(50)]
        paginator = _MockPaginator(data)
        result = await paginator()
        assert len(result.items) == LIST_VIEW_DEFAULT_PAGE_SIZE  # 20
        assert result.results_per_page == LIST_VIEW_DEFAULT_PAGE_SIZE
        assert result.cursor == 19
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_first_page_custom_page_size(self) -> None:
        """The caller can override the page size."""
        data = [str(i) for i in range(5)]
        paginator = _MockPaginator(data)
        result = await paginator(results_per_page=3)
        assert result.items == ["0", "1", "2"]
        assert result.results_per_page == 3
        assert result.cursor == 2
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_first_page_exact_fit(self) -> None:
        """When data size equals page size there should be no more results."""
        data = ["a", "b", "c"]
        paginator = _MockPaginator(data)
        result = await paginator(results_per_page=3)
        assert result.items == data
        assert result.has_more is False
        assert result.cursor == 2

    # ── cursor / continuation ──────────────────────────────────────

    @pytest.mark.asyncio
    async def test_next_page_via_cursor(self) -> None:
        """
        Passing a cursor returned from a previous page fetches the next
        batch of items.
        """
        data = [str(i) for i in range(10)]
        paginator = _MockPaginator(data)

        first = await paginator(results_per_page=4)
        assert first.items == ["0", "1", "2", "3"]
        assert first.cursor == 3
        assert first.has_more is True

        second = await paginator(cursor=first.cursor, results_per_page=4)
        assert second.items == ["4", "5", "6", "7"]
        assert second.cursor == 7
        assert second.has_more is True

        third = await paginator(cursor=second.cursor, results_per_page=4)
        assert third.items == ["8", "9"]
        assert third.cursor == 9
        assert third.has_more is False

    @pytest.mark.asyncio
    async def test_cursor_at_end_returns_empty(self) -> None:
        """A cursor that points beyond the last item yields an empty page."""
        data = ["x", "y"]
        paginator = _MockPaginator(data)
        result = await paginator(cursor=1, results_per_page=10)
        assert result.items == []
        assert result.cursor is None
        assert result.has_more is False

    # ── has_more facet ─────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_has_more_true_when_more_items_exist(self) -> None:
        data = [str(i) for i in range(25)]
        paginator = _MockPaginator(data)
        result = await paginator(results_per_page=20)
        assert result.has_more is True

    @pytest.mark.asyncio
    async def test_has_more_false_on_last_page(self) -> None:
        data = [str(i) for i in range(20)]
        paginator = _MockPaginator(data)
        result = await paginator(results_per_page=20)
        assert result.has_more is False

    @pytest.mark.asyncio
    async def test_has_more_false_when_data_is_exhausted(self) -> None:
        data = [str(i) for i in range(5)]
        paginator = _MockPaginator(data)
        result = await paginator(results_per_page=5)
        assert result.has_more is False

    # ── empty data ─────────────────────────────────────────────────

    @pytest.mark.asyncio
    async def test_empty_data_set(self) -> None:
        paginator = _MockPaginator([])
        result = await paginator()
        assert result.items == []
        assert result.cursor is None
        assert result.has_more is False
        assert result.results_per_page == LIST_VIEW_DEFAULT_PAGE_SIZE

    # ── default_page_size override ─────────────────────────────────

    @pytest.mark.asyncio
    async def test_custom_default_page_size(self) -> None:
        data = [str(i) for i in range(50)]
        paginator = _MockPaginator(data, default_page_size=5)
        result = await paginator()
        assert len(result.items) == 5
        assert result.results_per_page == 5
        assert result.cursor == 4
        assert result.has_more is True

    # ── Generic type erasure / runtime checks ──────────────────────

    def test_paginator_is_abstract(self) -> None:
        """AdvancedCursorPaginator cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AdvancedCursorPaginator()  # type: ignore[abstract]

    def test_subclass_with_concrete_types(self) -> None:
        """A subclass with concrete type arguments must be instantiable."""
        paginator = _MockPaginator([])
        assert isinstance(paginator, AdvancedCursorPaginator)