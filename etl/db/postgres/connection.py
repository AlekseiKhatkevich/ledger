import os
import secrets
from contextlib import asynccontextmanager, aclosing
from functools import cache, cached_property
from typing import AsyncGenerator, TypeVar

from sqlalchemy import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
)

from aux.mixins import Finalizable
from config import settings, BasePostgresSettings

__all__ = (
    'ledger_db',
)

T = TypeVar('T', bound=BasePostgresSettings)

@cache
class DB(Finalizable):
    def __init__(self, db_settings: T) -> None:
        self.db_settings: T = db_settings
        self.outer_connection: AsyncConnection | None = None
        self._cached_maker: async_sessionmaker |  None = None

    def _make_engine(self) -> AsyncEngine:
        # use NullPool for tests only
        match  self.db_settings.POOL_CLASS:
            case 'null':
                pool_class = NullPool
            case 'async':
                pool_class = AsyncAdaptedQueuePool

        engine_kwargs = dict(
            url=self.db_settings.PG_DSN,
            echo=self.db_settings.POSTGRES_ECHO,
            echo_pool=self.db_settings.ECHO_POOL,
            poolclass=pool_class,
            execution_options={'logging_token': f'connect#: {secrets.token_hex(3)}', },
            connect_args={'server_settings': {'application_name': f'{settings.APP_NAME}:{os.getpid()}'}},
        )
        if pool_class is AsyncAdaptedQueuePool:
            engine_kwargs |= dict (
                pool_pre_ping=self.db_settings.POOL_PRE_PING,
                pool_timeout=self.db_settings.POOL_TIMEOUT,
                pool_size=self.db_settings.POOL_SIZE,
                max_overflow=self.db_settings.POOL_MAX_OVERFLOW,
                pool_use_lifo=self.db_settings.POOL_USE_LIFO,
            )
        return create_async_engine(**engine_kwargs)

    @cached_property
    def engine(self) -> AsyncEngine:
        return self._make_engine()

    @asynccontextmanager
    async def make_outer_connection(self) -> AsyncGenerator[None]:
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

    @property
    async def finalize(self) -> None:
        await self.close()


ledger_db: DB[T]
def __getattr__(name: str) -> DB[T]:
    if name == 'ledger_db':
        return DB(db_settings=settings.DB.LEDGER)
    raise AttributeError(f'Module {__name__} has no attribute {name}')
