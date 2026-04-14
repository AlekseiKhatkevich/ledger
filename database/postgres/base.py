import datetime
import enum
from typing import Literal, Any

from sqlalchemy import TEXT
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(AsyncAttrs, MappedAsDataclass, DeclarativeBase, eq=False):
    type_annotation_map = {
        datetime.datetime: postgresql.TIMESTAMP(timezone=True),
        str: TEXT,
        enum.Enum: postgresql.ENUM(validate_strings=True, native_enum=True),
        Literal: postgresql.ENUM(validate_strings=True, native_enum=True),
    }

    @staticmethod
    def _asdict(instance) -> dict[str, Any]:
        return {c.name: getattr(instance, c.name) for c in instance.__table__.columns}

    def __eq__(self, other: Base) -> bool:
        return self._asdict(self) == self._asdict(other)