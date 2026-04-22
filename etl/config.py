from functools import cache

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    'settings',
)

class TemporalSettings:
    TEMPORAL_ADDRESS: str = 'temporal:7233'


class ExternalUrlsSettings:
    EXTERNAL_URL_COINS_LIST: HttpUrl


@cache
class Settings(
    TemporalSettings,
    ExternalUrlsSettings,
    BaseSettings,
):
    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        env_file=('secrets/ext_url/.env',  ),
        extra='ignore',
    )

settings: Settings
def __getattr__(name: str) -> Settings:
    if name == 'settings':
        return Settings()
    raise AttributeError(f'Module {__name__} has no attribute {name}')