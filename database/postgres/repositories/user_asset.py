import datetime

from functools import cache

import msgspec
import sqlalchemy as sa
from sqlalchemy import func, select, Integer
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased

import constants
from api.user_asset_operations.domain import UserAssetOperationDetailOut
from api.user_assets.domain import UserAssetData, GetUserAssetDetailInputParams, UserAssetDetailOut, \
    UserAssetDetailCombinedOut
from database.postgres.repositories.base_repository import PostgresBaseRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import UserAsset, AssetTickerPrice, AssetPopularity
from logic.repositories.user_asset import BaseUserAssetRepository


@cache
class PostgresUserAssetRepository(PostgresBaseRepository[UserAsset], BaseUserAssetRepository):
    model = UserAsset

    async def upsert(self, data: UserAssetData) ->  int | None:
        insert_stmt = insert(self.model).values(msgspec.to_builtins(data))
        on_conflict_stmt = insert_stmt.on_conflict_do_update(
            index_elements=['user_id', 'ticker_id',],
            set_=dict(name=insert_stmt.excluded.name),
            where=self.model.name.is_distinct_from(insert_stmt.excluded.name),
        ).returning(self.model.id)

        async with self.db.session() as session:
            resp = await session.scalar(on_conflict_stmt)
            await session.commit()
        return resp


    async def get_user_asset_detail(
            self,
            params: GetUserAssetDetailInputParams,
    ) -> UserAssetDetailCombinedOut | None:
        """
        Retrieve a single user asset enriched with price info and optional popularity rank.
        """
        operations_repo = PostgresUserAssetOperationRepository()

        stmt = select(
            self.model.id,
            self.model.name,
            self.model.ticker_id,
            AssetTickerPrice.price,
            func.coalesce(
                func.now() - AssetTickerPrice.updated_at > \
                datetime.timedelta(minutes=constants.ASSET_PRICE_CONSIDER_STALE_AFTER),
                True,
            ).label('outdated'),
            AssetTickerPrice.saved_at.label('time_when_price_was_update_in_db'),
        )

        if params.with_rank:
            popularity_subq = (
                select(
                    AssetPopularity.ticker_id,
                    func.dense_rank().over(
                        order_by=AssetPopularity.num_usages.desc(),
                    ).label('rank'),
                ).subquery()
            )
            popularity_alias = aliased(popularity_subq, name='ranked')
            stmt = stmt.add_columns(popularity_alias.c.rank.label('popularity_rank'))
            stmt = stmt.outerjoin(
                popularity_alias,
                UserAsset.ticker_id == popularity_alias.c.ticker_id,
            )
        else:
            stmt = stmt.add_columns(
                func.cast(sa.null(), Integer).label('popularity_rank'),
            )

        asset_stmt = stmt.outerjoin(
            AssetTickerPrice,
            self.model.ticker_id == AssetTickerPrice.name,
        ).where(
            self.model.user_id == params.user_id,
            self.model.ticker_id == params.ticker_id,
        )

        async with self.db.session() as session:
            row = await session.execute(asset_stmt)
            asset_result = row.one_or_none()
            if asset_result is None:
                return None
            row = await session.execute(
                operations_repo.get_user_asset_operations_stmt(
                    user_id=params.user_id,
                    user_asset_id=asset_result.id,
                    filters=params.op_filter
                )
            )
            operations_result = row.all()

        return UserAssetDetailCombinedOut(
            user_asset=msgspec.convert(
                asset_result, type=UserAssetDetailOut, from_attributes=True,
            ),
            operations=msgspec.convert(
                operations_result, type=list[UserAssetOperationDetailOut], from_attributes=True,
            )
        )

