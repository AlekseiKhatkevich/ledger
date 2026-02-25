import os
import secrets
import weakref
from contextlib import asynccontextmanager, aclosing
from functools import cache, cached_property
from typing import TYPE_CHECKING, AsyncGenerator

import anyio
import structlog
from litestar.serialization import decode_json, encode_json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from settings import settings

if TYPE_CHECKING:
    from sqlalchemy import URL

log = structlog.get_logger()


@cache
class DB:
    def __init__(self, url: URL | None = None) -> None:
        self.engine = create_async_engine(
            url or settings.pg_dsn,
            echo=settings.POSTGRES_ECHO,
            echo_pool=settings.ECHO_POOL,
            pool_pre_ping=settings.POOL_PRE_PING,
            pool_timeout=settings.POOL_TIMEOUT,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.POOL_MAX_OVERFLOW,
            pool_use_lifo=settings.POOL_USE_LIFO,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            execution_options={'logging_token': f'connect#: {secrets.token_hex(3)}',},
            connect_args={'server_settings': {'application_name': f'{settings.APP_NAME}:{os.getpid()}'}},
        )
        self._finalizer = weakref.finalize(self, lambda: anyio.run(self.close))

    @cached_property
    def _maker(self) -> async_sessionmaker:
        return async_sessionmaker(self.engine, expire_on_commit=False)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with aclosing(self._maker()) as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()
        await log.ainfo('Sqlalchemy engine has disposed')

    @property
    def pool_status(self) -> str:
        return self.engine.pool.status()

db: DB
def __getattr__(name: str) -> DB:
    if name == 'db':
        return DB()
    raise AttributeError(f'Module {__name__} has no attribute {name}')