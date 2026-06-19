import os
import secrets
import weakref
from contextlib import asynccontextmanager, aclosing
from functools import cache, cached_property
from typing import AsyncGenerator

import anyio
import structlog
from litestar.serialization import decode_json, encode_json
from sqlalchemy import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncEngine, AsyncSession,
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
        self._cached_maker: async_sessionmaker |  None = None
        if finalize:
            self._finalizer = weakref.finalize(self, lambda: anyio.run(self.close))

    @staticmethod
    def _make_engine() -> AsyncEngine:
        # use NullPool for tests only
        match settings.POOL_CLASS:
            case 'null':
                pool_class = NullPool
            case 'async':
                pool_class = AsyncAdaptedQueuePool

        # Add sslmode=disable to the DSN query string (asyncpg defaults to SSL,
        # but we connect through HAProxy which doesn't support PostgreSQL SSL)
        dsn = settings.PG_DSN.set(
            query={'sslmode': 'disable'},
        )
        engine_kwargs = dict(
            url=dsn,
            echo=settings.POSTGRES_ECHO,
            echo_pool=settings.ECHO_POOL,
            poolclass=pool_class,
            json_serializer=encode_json,
            json_deserializer=decode_json,
            execution_options={'logging_token': f'connect#: {secrets.token_hex(3)}', },
            connect_args={
                'server_settings': {'application_name': f'{settings.APP_NAME}:{os.getpid()}'},
            },
        )
        if pool_class is AsyncAdaptedQueuePool:
            engine_kwargs |= dict (
                pool_pre_ping=settings.POOL_PRE_PING,
                pool_timeout=settings.POOL_TIMEOUT,
                pool_size=settings.POOL_SIZE,
                max_overflow=settings.POOL_MAX_OVERFLOW,
                pool_use_lifo=settings.POOL_USE_LIFO,
            )
        return create_async_engine(**engine_kwargs)

    @cached_property
    def engine(self) -> AsyncEngine:
        return self._make_engine()

    @asynccontextmanager
    async def make_outer_connection(self) -> AsyncGenerator[None]:
        """
        https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#
        joining-a-session-into-an-external-transaction-such-as-for-test-suites

        Makes outer transaction and merges current session inside it as a savepoint.
        This behavior is similar to Django test suit.
        """
        self.outer_connection = await self.engine.connect()
        transaction = await self.outer_connection.begin()
        try:
            yield
        finally:
            await transaction.rollback()
            await self.outer_connection.close()
            self.outer_connection = None

    @property
    def _sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if self._cached_maker is None:
            self._cached_maker = async_sessionmaker(
                self.engine,
                expire_on_commit=False,
                join_transaction_mode='create_savepoint',
            )
        if self.outer_connection is not None:
            self._cached_maker.configure(bind=self.outer_connection)
        return self._cached_maker

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with aclosing(self._sessionmaker()) as async_session:
                yield async_session

    async def close(self, *_, **__) -> None:
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
