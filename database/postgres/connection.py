from functools import cache
from sqlalchemy.ext.asyncio import create_async_engine
# "postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase"
@cache
class DB:
    def __init__(self, conn_string):
        self.engine = create_async_engine(
            "postgresql+asyncpg:"
        )
