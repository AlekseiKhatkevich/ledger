from functools import cache

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings


@cache
class DB:
    def __init__(self, url: URL | None = None) -> None:
        self.engine = create_async_engine(
            url or settings.pg_dsn,
            echo=settings.ECHO,
            pool_pre_ping=settings.POOL_PRE_PING,
            pool_timeout=settings.POOL_TIMEOUT,
            pool_size=settings.POOL_SIZE,
            pool_max_overflow=settings.POOL_MAX_OVERFLOW,
            pool_use_lifo=settings.POOL_USE_LIFO,
        )
