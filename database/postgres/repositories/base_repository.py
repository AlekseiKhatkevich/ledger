from typing import Iterable

from sqlalchemy import select

from database.postgres.base import Base
from database.postgres.connection import db as _db, DB


class PostgresBaseRepository[T, bound=Base]:
    model: T

    def __init__(self, db: DB = _db) -> None:
        self.db = db

    async def get_by_field_names(self, **conditions) -> T:
        async with self.db.session() as session:
            return await session.scalar(select(self.model).filter_by(**conditions))

    async def get_by_id(self, /, _id: int) -> T:
        return await self.get_by_field_names(id=_id)

    async def add_all(self, models: Iterable[T]) -> Iterable[T]:
        async with self.db.session() as session:
            session.add_all(models)
            await session.commit()

        return models
