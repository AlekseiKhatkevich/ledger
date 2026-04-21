from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


@cache
class TemporalSettings(BaseSettings):
    TEMPORAL_ADDRESS: str

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra='ignore',
    )

