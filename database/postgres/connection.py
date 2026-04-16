import os
import secrets
import weakref
from contextlib import asynccontextmanager, aclosing
from functools import cache, cached_property
from typing import AsyncGenerator

import anyio
import structlog
from litestar.serialization import decode_json, encode_json
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncConnection,
    AsyncEngine,
)

from config import settings

log = structlog.get_logger()

__all__ = (
    'db',
)


@cache
class DB:
    def __init__(self, finalize: bool = False) -> None:
        self.outer_connection: AsyncConnection | None = None
        if finalize:
            self._finalizer = weakref.finalize(self, lambda: anyio.run(self.close))

    @staticmethod
    def _make_engine() -> AsyncEngine:
        return create_async_engine(
            settings.PG_DSN,
            echo=settings.POSTGRES_ECHO,
            echo_pool=settings.ECHO_POOL,
            pool_pre_ping=settings.POOL_PRE_PING,
            pool_timeout=settings.POOL_TIMEOUT,
            pool_size=settings.POOL_SIZE,
            max_overflow=settings.POOL_MAX_OVERFLOW,
            pool_use_lifo=settings.POOL_USE_LIFO,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            execution_options={'logging_token': f'connect#: {secrets.token_hex(3)}', },
            connect_args={'server_settings': {'application_name': f'{settings.APP_NAME}:{os.getpid()}'}},
    )

    @cached_property
    def engine(self) -> AsyncEngine:
        return self._make_engine()

    @asynccontextmanager
    async def make_outer_connection(self) -> AsyncGenerator[AsyncConnection]:
        """
        https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#
        joining-a-session-into-an-external-transaction-such-as-for-test-suites

        Makes outer transaction and joins current session inside it as a savepoint.
        This behavior is similar to Django test suit.
        """
        outer_engine = self._make_engine()
        self.outer_connection = await outer_engine.connect()
        transaction = await self.outer_connection.begin()
        try:
            yield self.outer_connection
        finally:
            await transaction.rollback()
            await self.outer_connection.close()
            self.outer_connection = None

    @cached_property
    def _maker(self) -> async_sessionmaker:
        return async_sessionmaker(
            bind=self.outer_connection or self.engine,
            expire_on_commit=False,
            join_transaction_mode='create_savepoint',
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with aclosing(self._maker()) as session:
            yield session

    async def close(self, *args, **kwargs) -> None:
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
