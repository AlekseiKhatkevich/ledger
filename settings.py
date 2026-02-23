from functools import cached_property, cache
from pathlib import Path

from pydantic import PostgresDsn
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings:
    POSTGRES_PASSWORD_FILE: str
    POSTGRES_USER_FILE: str
    POSTGRES_DB_FILE: str
    PGHOSTADDR: str

    model_config = SettingsConfigDict(secrets_dir='/run/secrets',)

    @computed_field
    @cached_property
    def pg_dsn(self) -> PostgresDsn:
        """Reading Postgres credentials from docker secrets."""
        pwd = Path(self.POSTGRES_PASSWORD_FILE).read_text()
        usr = Path(self.POSTGRES_USER_FILE).read_text()
        db = Path(self.POSTGRES_DB_FILE).read_text()
        return PostgresDsn(
            f'postgresql+asyncpg://{usr}:{pwd}@{self.PGHOSTADDR}:5432/{db}'
        )

@cache
class Settings(PostgresSettings, BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/postgres/.env', '.env.prod'),
    )

settings: Settings

def __getattr__(name: str) -> Settings:
    if name == 'settings':
        return Settings()
    raise AttributeError(f'Module {__name__} has no attribute {name}')