import datetime
import decimal
import functools
import inspect
from collections.abc import Callable
from functools import cache
from typing import Any, Awaitable, ParamSpec, TypeVar

from sqlalchemy import MetaData, VARCHAR, BIGINT, Integer, select, func, values, column, except_, String
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, aliased

import constants
from db.postgres.connection import ledger_db
from repositories.database.domain.ledger import LedgerPricesFromDB

metadata = MetaData()
LedgerBase = automap_base(metadata=metadata)


class Base(DeclarativeBase):
    metadata = metadata

#  automap doesn't work here as model doesn't have a primary key of any sort
class AssetPopularity(Base):
    __tablename__ = "asset_popularity"
    is_view = True

    ticker_id: Mapped[str] = mapped_column(VARCHAR(50), primary_key=True)
    num_usages: Mapped[int] = mapped_column(BIGINT)

#  system view pg_locks
class PgLocks(Base):
    __tablename__ = "pg_locks"
    is_view = True

    classid: Mapped[int]
    objid: Mapped[int]
    locktype: Mapped[str]

    __mapper_args__ = {"primary_key": ["classid", "objid", "locktype"],}


M = TypeVar('M', bound=DeclarativeBase)
P = ParamSpec('P')
R = TypeVar('R')
C = TypeVar('C', bound=type)


def with_prepare_automap(cls) -> C:
    """Calls `DB.prepare_automap` to fill data in Base before each method call."""

    def make_wrapped(fn: Callable[P, Awaitable[R] | R]) -> Any:
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
        tickers: list[str],
        batch_size: int,
        lock_namespace: int = constants.LEDGER_PRICES_LOCK_NAMESPACE,
        age_interval: datetime.timedelta = constants.LEDGER_PRICES_PRICE_TIMEOUT,
    ) -> list[LedgerPricesFromDB]:

        atp = aliased(self.asset_tickers_price_model)
        pop = aliased(AssetPopularity)

        #  query 1
        locked = select(PgLocks).where(
                PgLocks.classid == lock_namespace,
                PgLocks.objid == atp.id,
                PgLocks.locktype == "advisory",
            ).exists()

        query = select(
            atp.name,
            atp.price,
            atp.updated_at,
            atp.id,
            func.pg_try_advisory_lock(lock_namespace, atp.id.cast(Integer)).label('acquired'),
        ).select_from(atp).outerjoin(
            pop, atp.name == pop.ticker_id,
        ).where(
            atp.updated_at < func.now() - age_interval,
            ~ locked,
        ).order_by(
            atp.name.in_(tickers).desc(),
            pop.num_usages.desc().nullslast(),
        )

        #  query 2 , find tickets that are not in asset_ticker_price yet.
        value_expr = (
            values(
                column("name", String),
                name='input_tickers'
            ).data(
                [(t,) for t in tickers]
            )
        )
        input_select = value_expr.select()
        existing_select = select(atp.name)
        missing_tickers_query = except_(input_select, existing_select)

        async with self.db.session() as session:
            result = await session.scalars(missing_tickers_query)
            ticker_names_not_in_db_yet = result.all()

            query = query.limit(batch_size - len(ticker_names_not_in_db_yet))
            result = await session.execute(query)

        existing_prices = [
            LedgerPricesFromDB(
                name=row.name,
                price=row.price,
                updated_at=row.updated_at,
                id=row.id,
            )
            for row in result.all()
        ]
        non_existing_prices = [
            LedgerPricesFromDB(
                name=name,
                price=decimal.Decimal(0),
                updated_at=datetime.datetime.min.replace(tzinfo=datetime.UTC),
                id=None,
            )
            for name in ticker_names_not_in_db_yet
        ]

        return [*existing_prices, *non_existing_prices]

    async def pg_advisory_unlock_all(self) -> None:
        async with self.db.session() as session:
            await session.execute(func.pg_advisory_unlock_all())

    async def update_prices(
        self,
        tickers_with_prices: list[LedgerPricesFromDB],
        ticker_names: set[str],
    ) -> list[LedgerPricesFromDB]:
        """Upsert ticker prices via CTE and return requested tickers in one query."""
        values_to_insert = [
            {
                'name': t.name,
                'price': t.price,
                'updated_at': t.updated_at,
                'saved_at': func.NOW(),
            }
            for t in tickers_with_prices
        ]

        insert_stmt = insert(self.asset_tickers_price_model).values(values_to_insert)
        excluded = insert_stmt.excluded

        upsert_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['name', ],
            set_={
                'price': excluded.price,
                'updated_at': excluded.updated_at,
                'saved_at': func.NOW(),
            },
            where=(
                self.asset_tickers_price_model.updated_at < excluded.updated_at
            ),
        )

        select_stmt = select(
            self.asset_tickers_price_model,
        ).where(
            self.asset_tickers_price_model.name.in_(ticker_names),
        )

        async with self.db.session() as session:
            await session.execute(upsert_stmt)
            result = await session.execute(select_stmt)
            await session.commit()

        rows = result.scalars().all()
        return [
            LedgerPricesFromDB(
                name=row.name,
                price=row.price,
                updated_at=row.updated_at,
                id=row.id,
            )
            for row in rows
        ]