import dataclasses


@dataclasses.dataclass(frozen=True)
class PaginationParams[T]:
    cursor: T | None
    results_per_page: int


@dataclasses.dataclass(frozen=True)
class PaginatedPage[T]:
    items: list[T]
    cursor: str | float | int | None  # id of the last item on this page
    has_more: bool                    # whether a next page exists

