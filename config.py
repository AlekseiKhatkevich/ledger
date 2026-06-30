from functools import cached_property, cache
from typing import Literal, Any, ChainMap

from pydantic import computed_field, PositiveInt, PositiveFloat, HttpUrl, SecretStr
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from sqlalchemy import URL

import constants
from aux.openbao.client import SyncOpenBaoClient


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


# noinspection HttpUrlsUsage
class KeycloakSettings:
    """Keycloak auth server settings"""
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID: str
    KEYCLOAK_CLIENT_SECRET: str
    KEYCLOAK_POOL_MAXSIZE: PositiveInt
    KEYCLOAK_API_KEY_HEADER: str
    KEYCLOAK_API_KEY_HEADER_PREFIX: str
    KEYCLOAK_DOMAIN: str
    KEYCLOAK_PORT: PositiveInt
    KEYCLOAK_SCHEME: str
    KEYCLOAK_ADMIN: str
    KEYCLOAK_ADMIN_PASSWORD: str

    @computed_field
    @cached_property
    def KEYCLOAK_SERVER_URL(self) -> str:
        """Url to Keycloak auth server"""
        #  From inside always use http as we have ssl termination inside Caddy proxy
        return f'http://{self.KEYCLOAK_DOMAIN}:{self.KEYCLOAK_PORT}/'


class ApiSettings:
    API_SCHEMA_ENDPOINT: str = '/docs'


class NNGSettings:
    NNG_BASE_ENTRYPOINT_ADR: str = 'abstract://entrypoint_socket'
    NNG_INIT_TIME_INTERVAL: float = 0.2
    NNG_KNOWN_MESSAGES_QTY: PositiveInt = 300
    NNG_RECV_TIMEOUT: PositiveInt = 500
    NNG_SURVEY_ADDR: str = 'abstract://survey'
    NNG_SURVEY_INTERVAL: float = 1.0


class TemporalSettings:
    TEMPORAL_ADDRESS: str = 'temporal:7233'
    TEMPORAL_NAMESPACE: str = 'default'


class OpenBaoSettings:
    BAO_UNSEAL_KEYS: tuple[SecretStr, ...]
    BAO_ROOT_KEY: SecretStr
    BAO_ACCESS_ADDR: HttpUrl
    BAO_APPROLE_ID: SecretStr
    BAO_APPROLE_SECRET_ID: SecretStr
    BAO_KV_MOUNT_POINT: str = 'ledger'


class OpenBaoSettingsFinal(OpenBaoSettings, BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/openbao/.env',),
        extra='ignore',
    )


class OpenBaoSettingsSource(PydanticBaseSettingsSource):

    @cache
    def _load_openbao_settings(self) -> ChainMap[str, str]:
        client = SyncOpenBaoClient(settings=OpenBaoSettingsFinal())
        response = client.read_secrets_batch(constants.OPENBAO_PATHS)
        return response.response_dict

    def get_field_value(
            self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        loaded_openbao_settings = self._load_openbao_settings()
        field_value = loaded_openbao_settings.get(field_name)
        return field_value, field_name, False

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value
        return d


@cache
class Settings(
    OpenBaoSettings,
    ApiSettings,
    PostgresSettings,
    KeycloakSettings,
    NNGSettings,
    TemporalSettings,
    BaseSettings,
):
    """Combined settings"""
    APP_NAME: str = 'ledger-backend'
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=(
            'secrets/postgres/.env',
            'secrets/keycloak/.env',
            'secrets/openbao/.env',
        ),
        extra='ignore',
    )

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            OpenBaoSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

settings: Settings
openbao_settings: OpenBaoSettingsFinal
def __getattr__(name: str) -> Settings | OpenBaoSettingsFinal:
    if name == 'settings':
        return Settings()
    elif name == 'openbao_settings':
        return OpenBaoSettingsFinal()
    raise AttributeError(f'Module {__name__} has no attribute {name}')