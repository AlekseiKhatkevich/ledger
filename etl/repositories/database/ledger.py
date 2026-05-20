import functools
import inspect
from functools import cache
from typing import TypeVar, Callable, ParamSpec, Awaitable

from sqlalchemy import MetaData, Table, Column, VARCHAR, BIGINT
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import DeclarativeBase

from db.postgres.connection import ledger_db

metadata = MetaData()
LedgerBase = automap_base(metadata=metadata)


M = TypeVar('M', bound=DeclarativeBase)
P = ParamSpec('P')
R = TypeVar('R')
C = TypeVar('C', bound=type)


#  as asset_popularity does not have a primary key automap can not load it, so we map it ourselves.
Table(
    "asset_popularity",
    metadata,
    Column("ticker_id", VARCHAR(50), primary_key=True),
    Column("num_usages", BIGINT),
)

def with_prepare_automap(cls) -> C:
    """Calls `DB.prepare_automap` to fill data in Base before each method call."""

    def make_wrapped(fn: Callable[P, Awaitable[R] | R]) -> Callable[P, Awaitable[R] | R]:
        @functools.wraps(fn)
        async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[R] | R:
            async with self.db.prepare_automap(self.base):
                if inspect.iscoroutinefunction(fn):
                    return await fn(self, *args, **kwargs)
                else:
                    return fn(self, *args, **kwargs)

        return wrapped

    for name, val in vars(cls).items():
        if name.startswith('__') and name.endswith('__'):
            continue
        if not callable(val):
            continue

        setattr(cls, name, make_wrapped(val))

    return cls

@cache
@with_prepare_automap
class LedgerDbRepository:
    def __init__(self) -> None:
        self._automap_completed = False
        self.db = ledger_db
        self.base = LedgerBase

    @property
    def asset_tickers_model(self) -> M:
        return self.base.classes.asset_tickers

    @property
    def asset_tickers_price_model(self) -> M:
        return self.base.classes.asset_tickers_price

    @property
    def asset_popularity(self) -> M:
        return self.base.classes.asset_popularity

    async def upsert_tickers(self, tickers: frozenset[str]) -> None:
        insert_stmt = insert(self.asset_tickers_model).values(tuple({'name': t.upper()} for t in tickers))
        on_conflict_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['name',])
        async with self.db.session() as session:
            await session.execute(on_conflict_stmt)
            await session.commit()
