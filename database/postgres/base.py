import enum
from typing import Literal

from sqlalchemy import TEXT
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
import datetime
from sqlalchemy.dialects import postgresql


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: postgresql.TIMESTAMP(timezone=True),
        str: TEXT,
        enum.Enum: postgresql.ENUM(validate_strings=True, native_enum=True),
        Literal: postgresql.ENUM(validate_strings=True, native_enum=True),
    }

