from typing import Any

from sqlalchemy import select

from database.postgres.base import Base
from database.postgres.connection import db as _db, DB


class PostgresBaseRepository[T, bound=Base]:
    model: T

    def __init__(self, db: DB = _db) -> None:
        self.db = db

    async def _get_by_field_name(self, field_name: str, value: Any) -> T:
        field = getattr(self.model, field_name)
        async with self.db.session() as session:
            return await session.scalar(select(self.model).where(field == value))

    async def get_by_id(self, _id: str) -> T:
        return await self._get_by_field_name('id', _id)
