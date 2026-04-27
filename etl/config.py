from functools import cache, cached_property
from typing import Literal

from pydantic import HttpUrl, computed_field, PositiveFloat, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

__all__ = (
    'settings',
    'BasePostgresSettings',
)


class TemporalSettings:
    TEMPORAL_ADDRESS: str = 'temporal:7233'
    TEMPORAL_NAMESPACE: str = 'default'


class ExternalUrlsSettings:
    EXTERNAL_URL_COINS_LIST: HttpUrl


class BasePostgresSettings:
    PGPASSWORD: str
    PGUSER: str
    PGDATABASE: str
    PGHOSTADDR: str
    POSTGRES_ECHO: bool = True
    POOL_PRE_PING: bool = True
    POOL_TIMEOUT: PositiveFloat = 10.0
    POOL_SIZE: PositiveInt = 2
    POOL_MAX_OVERFLOW: PositiveInt = 10
    POOL_USE_LIFO: bool = True
    ECHO_POOL: bool = True
    POOL_CLASS: Literal['null', 'async'] = 'async'

    @computed_field
    @cached_property
    def PG_DSN(self) -> URL:
        """Reading Postgres credentials from docker secrets or env."""
        return URL.create(
            'postgresql+asyncpg',
            username=self.PGUSER,
            password=self.PGPASSWORD,
            host=self.PGHOSTADDR,
            database=self.PGDATABASE,
        )


class LedgerPostgresSettings(BasePostgresSettings, BaseSettings):
    model_config = SettingsConfigDict(frozen=True)


class DbSettings(BaseSettings):
    LEDGER: LedgerPostgresSettings

@cache
class Settings(
    TemporalSettings,
    ExternalUrlsSettings,
    BaseSettings,
):
    DB: DbSettings
    APP_NAME: str = 'temporal_worker'

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/ext_url/.env', 'secrets/db/ledger/.env', ),
        extra='ignore',
        env_nested_delimiter='__',
    )

settings: Settings
def __getattr__(name: str) -> Settings:
    if name == 'settings':
        return Settings()
    raise AttributeError(f'Module {__name__} has no attribute {name}')