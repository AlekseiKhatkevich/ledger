from functools import cached_property, cache

from pydantic import computed_field, PositiveInt, PositiveFloat, AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresSettings:
    """PostgesDB settings"""
    PGPASSWORD: str
    PGUSER: str
    PGDATABASE: str
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
    def PG_DSN(self) -> URL:
        """Reading Postgres credentials from docker secrets or env."""
        return URL.create(
            'postgresql+asyncpg',
            username=self.PGUSER,
            password=self.PGPASSWORD,
            host=self.PGHOSTADDR,
            database=self.PGDATABASE,
        )


class KeycloakSettings:
    """Keycloak auth server settings"""
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_POOL_MAXSIZE: PositiveInt
    KEYCLOAK_API_KEY_HEADER: str
    KEYCLOAK_DOMAIN: str
    KEYCLOAK_PORT: PositiveInt
    KEYCLOAK_SCHEME: str

    @computed_field
    @cached_property
    def KEYCLOAK_SERVER_URL(self) -> str:
        """Url to Keycloak auth server"""
        return f'{self.KEYCLOAK_SCHEME}://{self.KEYCLOAK_DOMAIN}:{self.KEYCLOAK_PORT}/'


class ApiSettings:
    API_SCHEMA_ENDPOINT: str = '/docs'

@cache
class Settings(
    ApiSettings,
    PostgresSettings,
    KeycloakSettings,
    BaseSettings,
):
    """Combined settings"""
    APP_NAME: str = 'ledger'
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/postgres/.env', 'secrets/keycloak/.env', ),
        extra='ignore',
    )

settings: Settings
def __getattr__(name: str) -> Settings:
    if name == 'settings':
        return Settings()
    raise AttributeError(f'Module {__name__} has no attribute {name}')