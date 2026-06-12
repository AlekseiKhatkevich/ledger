import dataclasses


@dataclasses.dataclass(frozen=True)
class PaginationParams:
    cursor: int | str| None
    results_per_page: int


@dataclasses.dataclass(frozen=True)
class PaginatedPage[T]:
    items: list[T]
    cursor: str | None  # ticker_id of the last item on this page
    has_more: bool               # whether a next page exists

