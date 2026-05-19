"""
DDLElement-based helpers for pg_ivm (Incremental Materialized Views).

Provides SQLAlchemy DDLElement classes that compile to pg_ivm function calls::

    from sqlalchemy import select, func
    from database.postgres.pgivm import CreateImmv, DropImmv, BaseImmvORMMixin

    # Standalone usage:
    op.execute(CreateImmv("my_view", selectable))

    # ORM mixin usage:
    class MyView(Base, BaseImmvORMMixin):
        __table__ = sa.Table(...)
        selectable = ...
        MyView.create(op)
        MyView.drop(op)
"""

import sqlalchemy as sa
from alembic.operations import Operations
from sqlalchemy import DDLElement, Select, Selectable
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import compiler
from sqlalchemy.sql import ClauseElement
from sqlalchemy.sql.compiler import SQLCompiler


def _compile_query(
    stmt: ClauseElement,
    dialect: type[postgresql.dialect] = postgresql.dialect,
) -> str:
    """Compile a SQLAlchemy statement into a SQL string without literal binds."""
    compiled = stmt.compile(
        dialect=dialect(),
        compile_kwargs={"literal_binds": True},
    )
    return str(compiled)


class CreateImmv(DDLElement):
    """``SELECT pgivm.create_immv('name', '<sql>')``"""

    def __init__(
        self,
        name: str,
        selectable: Select | Selectable,
    ) -> None:
        self.name = name
        self.selectable = selectable


@compiler.compiles(CreateImmv)
def _compile_create_immv(
    element: CreateImmv,
    compiler: SQLCompiler,
    **kw: object,
) -> str:
    sql = _compile_query(element.selectable)
    return f"SELECT pgivm.create_immv('{element.name}', '{sql}');"


class RefreshImmv(DDLElement):
    """``SELECT pgivm.refresh_immv('name', with_data)``"""

    def __init__(
        self,
        name: str,
        with_data: bool = True,
    ) -> None:
        self.name = name
        self.with_data = with_data


@compiler.compiles(RefreshImmv)
def _compile_refresh_immv(
    element: RefreshImmv,
    compiler: SQLCompiler,
    **kw: object,
) -> str:
    return f"SELECT pgivm.refresh_immv('{element.name}', {str(element.with_data).lower()});"


class DropImmv(DDLElement):
    """``DROP TABLE name`` (pg_ivm cleans up the catalog automatically)."""

    def __init__(
        self,
        name: str,
        if_exists: bool = True,
    ) -> None:
        self.name = name
        self.if_exists = if_exists


@compiler.compiles(DropImmv)
def _compile_drop_immv(
    element: DropImmv,
    compiler: SQLCompiler,
    **kw: object,
) -> str:
    if_exists = "IF EXISTS " if element.if_exists else ""
    return f"DROP TABLE {if_exists}{element.name};"


class GetImmvDef(DDLElement):
    """``SELECT pgivm.get_immv_def('name')`` — returns the view definition as text."""

    def __init__(self, name: str) -> None:
        self.name = name


@compiler.compiles(GetImmvDef)
def _compile_get_immv_def(
    element: GetImmvDef,
    compiler: SQLCompiler,
    **kw: object,
) -> str:
    return f"SELECT pgivm.get_immv_def('{element.name}');"


class BaseImmvORMMixin:
    """Mixin for ORM models backed by an IMMV.

    Usage::

        from database.postgres.pgivm import BaseImmvORMMixin
        from database.postgres.base import Base

        class AssetPopularity(BaseImmvORMMixin, Base):
            __tablename__ = "asset_popularity"
            is_view = True

            ticker_id: Mapped[str] = mapped_column(primary_key=True)
            num_usages: Mapped[int]

            selectable = select(
                UserAsset.ticker_id,
                func.count().label("num_usages"),
            ).select_from(UserAsset).group_by(UserAsset.ticker_id)

            # Then in alembic migration:
            AssetPopularity.create(op)
            AssetPopularity.drop(op)
    """

    selectable: Select | Selectable | None = None
    __tablename__: str
    is_view: bool = True

    @classmethod
    def create(cls, op: Operations) -> None:
        """Create the IMMV. Use in alembic upgrade."""
        if cls.selectable is None:
            raise TypeError(f"{cls.__name__}.selectable must be set")
        if not hasattr(cls, '__tablename__') or cls.__tablename__ is None:
            raise TypeError(f"{cls.__name__}.__tablename__ must be set")
        op.execute(CreateImmv(cls.__tablename__, cls.selectable))

    @classmethod
    def drop(cls, op: Operations) -> None:
        """Drop the IMMV. Use in alembic downgrade."""
        if not hasattr(cls, '__tablename__') or cls.__tablename__ is None:
            raise TypeError(f"{cls.__name__}.__tablename__ must be set")
        op.execute(DropImmv(cls.__tablename__))
