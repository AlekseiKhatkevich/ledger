import datetime
import enum
from typing import Literal, Any

from sqlalchemy import TEXT
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    type_annotation_map = {
        datetime.datetime: postgresql.TIMESTAMP(timezone=True),
        str: TEXT,
        enum.Enum: postgresql.ENUM(validate_strings=True, native_enum=True),
        Literal: postgresql.ENUM(validate_strings=True, native_enum=True),
    }

    def as_fields_dict(self, exclude: set | None = None) -> dict[str, Any]:
        # noinspection PyTypeChecker
        exclude = exclude or set()
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns if c.name not in exclude
        }
