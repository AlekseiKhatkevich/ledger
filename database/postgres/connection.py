from functools import cache
from typing import Protocol

from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings


class SupportsStr(Protocol):
    def __str__(self) -> str:...

@cache
class DB:
    def __init__(self, conn_string: SupportsStr | None = None) -> None:
        self.engine = create_async_engine(str(conn_string or settings.pg_dsn))
