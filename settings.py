from functools import cached_property
from pathlib import Path

from pydantic import PostgresDsn
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings:
    POSTGRES_PASSWORD_FILE: str
    POSTGRES_USER_FILE: str
    POSTGRES_DB_FILE: str

    model_config = SettingsConfigDict(secrets_dir='/run/secrets')

    @computed_field
    @cached_property
    def pg_dsn(self) -> PostgresDsn:
        pwd = Path(self.POSTGRES_PASSWORD_FILE).read_text()
        usr = Path(self.POSTGRES_USER_FILE).read_text()
        db = Path(self.POSTGRES_DB_FILE).read_text()
        return PostgresDsn(
            f'postgresql+asyncpg://{usr}:{pwd}@localhost:5432/{db}'
        )


class Settings(PostgresSettings, BaseSettings):
    pass

