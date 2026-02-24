import secrets
from functools import cache
import os
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine

from settings import settings


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
            execution_options={
                'logging_token': f'connect#: {secrets.token_hex(3)}',
            },
            connect_args={
                'server_settings': {'application_name': f'{settings.APP_NAME}:{os.getpid()}'}
            }
        )

    async def close(self) -> None:
        await self.engine.dispose()

    @property
    def pool_status(self) -> str:
        return self.engine.pool.status()



# todo call .dispose() via weak ref and call close via lifecycle