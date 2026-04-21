from functools import cached_property, cache
from typing import Literal

from pydantic import computed_field, PositiveInt, PositiveFloat
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


@cache
class TemporalSettings(BaseSettings):
    TEMPORAL_ADDRESS: str

    model_config = SettingsConfigDict(
        env_ignore_empty=True,
        extra='ignore',
    )

