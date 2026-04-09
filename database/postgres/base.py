import enum
from typing import Literal

from sqlalchemy import TEXT
from sqlalchemy.orm import DeclarativeBase
import datetime
from sqlalchemy.dialects import postgresql


class Base(DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: postgresql.TIMESTAMP(timezone=True),
        str: TEXT,
        enum.Enum: postgresql.ENUM(validate_strings=True, native_enum=True),
        Literal: postgresql.ENUM(validate_strings=True, native_enum=True),
    }

