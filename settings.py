from functools import cached_property, cache
from pathlib import Path

from pydantic import computed_field, PositiveInt, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresSettings:
    POSTGRES_PASSWORD_FILE: str
    POSTGRES_USER_FILE: str
    POSTGRES_DB_FILE: str
    PGHOSTADDR: str
    POSTGRES_ECHO: bool = True
    POOL_PRE_PING: bool = True
    POOL_TIMEOUT: PositiveFloat = 10.0
    POOL_SIZE: PositiveInt = 3
    POOL_MAX_OVERFLOW: PositiveInt = 20
    POOL_USE_LIFO: bool = True
    ECHO_POOL: bool = True

    @computed_field
    @cached_property
    def pg_dsn(self) -> URL:
        """Reading Postgres credentials from docker secrets."""
        pwd = Path(self.POSTGRES_PASSWORD_FILE).read_text()
        usr = Path(self.POSTGRES_USER_FILE).read_text()
        db = Path(self.POSTGRES_DB_FILE).read_text()
        return URL.create(
            'postgresql+asyncpg',
            username=usr,
            password=pwd,
            host=self.PGHOSTADDR,
            database=db,
        )

@cache
class Settings(PostgresSettings, BaseSettings):
    APP_NAME: str = 'ledger'

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/postgres/.env', '.env.prod'),
        secrets_dir='/run/secrets',
        extra='ignore',
    )

settings: Settings
def __getattr__(name: str) -> Settings:
    if name == 'settings':
        return Settings()
    raise AttributeError(f'Module {__name__} has no attribute {name}')