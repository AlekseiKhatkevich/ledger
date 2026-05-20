import datetime
import functools
import inspect
from functools import cache
from typing import TypeVar, Callable, ParamSpec, Awaitable

from sqlalchemy import MetaData, VARCHAR, BIGINT, Integer, select, func, case, true
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased
from sqlalchemy.sql import text
import constants

from db.postgres.connection import ledger_db

metadata = MetaData()
LedgerBase = automap_base(metadata=metadata)


class Base(DeclarativeBase):
    metadata = metadata


class AssetPopularity(Base):
    __tablename__ = "asset_popularity"

    ticker_id: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    num_usages: Mapped[int] = mapped_column(BIGINT)


M = TypeVar('M', bound=DeclarativeBase)
P = ParamSpec('P')
R = TypeVar('R')
C = TypeVar('C', bound=type)

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
    def asset_popularity_model(self) -> M:
        return self.base.classes.asset_popularity

    async def upsert_tickers(self, tickers: frozenset[str]) -> None:
        insert_stmt = insert(self.asset_tickers_model).values(tuple({'name': t.upper()} for t in tickers))
        on_conflict_stmt = insert_stmt.on_conflict_do_nothing(index_elements=['name',])
        async with self.db.session() as session:
            await session.execute(on_conflict_stmt)
            await session.commit()

    async def get_prices_batch(
        self,
        tickers: tuple[str, ...],
        batch_size: int,
        lock_namespace: int = constants.LEDGER_PRICES_LOCK_NAMESPACE,
        age_interval: datetime.timedelta = constants.LEDGER_PRICES_PRICE_TIMEOUT,
    ) -> list[dict]:
        """Select up to batch_size price records, forcing tickers to appear first."""

        atp = aliased(self.asset_tickers_price_model)
        pop = aliased(AssetPopularity)

        inner = select(
            atp.id,
            atp.name,
            atp.price,
            atp.updated_at,
            pop.num_usages,
            func.pg_try_advisory_lock(lock_namespace, atp.id.cast(Integer)).label('acquired'),
        ).select_from(
            atp
        ).outerjoin(
            pop, atp.name == pop.ticker_id,
        ).where(
            atp.updated_at < func.now() - age_interval,
        ).order_by(
            case((atp.name.in_(tickers), 1), else_=0).desc(),
            pop.num_usages.desc().nullslast(),
        ).limit(batch_size).subquery()

        outer = select(
            inner.c.id,
            inner.c.name,
            inner.c.price,
            inner.c.updated_at,
            inner.c.num_usages,
        ).where(inner.c.acquired == true())

        async with self.db.session() as session:
            result = await session.execute(outer)
            rows = [dict(r._mapping) for r in result]
            await session.execute(text("SELECT pg_advisory_unlock_all()"))
            await session.commit()
        return rows
