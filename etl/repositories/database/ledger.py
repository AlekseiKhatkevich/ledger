import functools
import inspect
from functools import cache
from typing import TypeVar, Callable, ParamSpec, Awaitable

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import DeclarativeBase

from db.postgres.connection import ledger_db

LedgerBase = automap_base()


M = TypeVar('M', bound=DeclarativeBase)
P = ParamSpec('P')
R = TypeVar('R')
C = TypeVar('C', bound=type)

def with_prepare_automap(cls) -> C:

    def make_wrapped(fn: Callable[P, Awaitable[R] | R]) -> Callable[P, Awaitable[R] | R]:
        @functools.wraps(fn)
        async def wrapped(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[R] | R:
            if not self._automap_completed:
                await self.db.prepare_automap(self.base)
                self._automap_completed = True

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
    def model(self) -> M:
        return self.base.classes.asset_tickers

    async def upsert_tickers(self, tickers: frozenset[str]) -> None:
        insert_stmt = insert(self.model).values(tuple({'name': t.upper()} for t in tickers))
        on_conflict_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['name'])
        async with self.db.session() as session:
            await session.execute(on_conflict_stmt)
            await session.commit()
