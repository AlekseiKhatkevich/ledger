from database.postgres.base import Base
from database.postgres.connection import db as _db, DB

class PostgresBaseRepository[T, bound=Base]:
    model: T

    def __init__(self, db: DB = _db) -> None:
        self.db = DB()
