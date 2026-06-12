import abc
from typing import Iterable, Any
from typing import Protocol

from advanced_alchemy.filters import StatementFilter
from sqlalchemy import select, Executable

from database.postgres.base import Base
from database.postgres.connection import db as _db, DB


class FilterBase(Protocol):
    @property
    @abc.abstractmethod
    def alchemy_filters(self)  -> Iterable[StatementFilter]:
        pass

class PostgresBaseRepository[T, bound=Base]:
    model: T

    def __init__(self, db: DB = _db) -> None:
        self.db = db

    def apply_filters[S: Executable, F: FilterBase](self, stmt: S, filters: F, model: T | None = None) -> S:
        model = model or self.model

        for alchemy_filter in filters.alchemy_filters:
            stmt = alchemy_filter.append_to_statement(stmt, model)

        return stmt

    async def get_by_field_names(self, **conditions) -> T:
        async with self.db.session() as session:
            return await session.scalar(select(self.model).filter_by(**conditions))

    async def get_by_id(self, /, _id: int) -> T:
        return await self.get_by_field_names(id=_id)

    async def add_all(self, models: Iterable[T]) -> list[T]:
        async with self.db.session() as session:
            session.add_all(models)
            await session.commit()

        return models

    async def get_all(self) -> list[T]:
        async with self.db.session() as session:
            res = await session.scalars(select(self.model))
            return res.all()

    @staticmethod
    def paginate_items(
            items: list,
            results_per_page: int,
            cursor_field: str,
    ) -> tuple[list, bool, Any | None]:
        if len(items) > results_per_page:
            has_more = True
            items = items[:results_per_page]
        else:
            has_more = False

        new_cursor = getattr(items[-1], cursor_field) if items else None

        return items, has_more, new_cursor
