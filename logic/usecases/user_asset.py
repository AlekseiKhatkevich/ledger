from decimal import Decimal
import uuid

import polars as pl

from api.user_asset_operations.domain import UserAssertOperationsSummaryOut, UserAssetOperationSummaryGrouped
from api.user_assets.domain import UserAssetData, UserAssetAggregatedPage, GetUserAssetDetailInputParams, \
    UserAssetDetailCombinedOut
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.exceptions import UserAssetAddressNotFoundError


class UserAssetUpsertUseCase:

    @staticmethod
    async def execute(data: UserAssetData) ->  int | None:
        return await PostgresUserAssetRepository().upsert(data)


class UserAssetListUseCase:

    @staticmethod
    async def execute(
            user_id: uuid.UUID,
            cursor: str | None,
            page_size: int,
    ) -> UserAssetAggregatedPage:
        return await PostgresUserAssetOperationRepository().get_user_asset_aggregates(
            user_id,
            page_size,
            cursor,
        )

class UserAssetDetailUseCase:

    def _calculate_operations_summary(
            self,
            asset_data_from_db: UserAssetDetailCombinedOut,
    ) -> UserAssertOperationsSummaryOut:
        df = pl.DataFrame(
            asset_data_from_db.operations,
            schema_overrides={
                "quantity": pl.Decimal(scale=10),
                "unit_price": pl.Decimal(scale=10),
                "summ": pl.Decimal(scale=10),
            },
        )
        agg_exprs = [
            pl.len().alias("count"),
            pl.sum("quantity").alias("total_quantity"),
            pl.sum("summ").alias("total_summ"),
        ]
        overall = [
            UserAssetOperationSummaryGrouped(key=r['type'], **r)
            for r in df.group_by('type').agg(*agg_exprs).to_dicts()
        ]
        by_public_key = [
            UserAssetOperationSummaryGrouped(key=r.pop('public_key'), **r)
            for r in df.group_by('public_key', 'type').agg(*agg_exprs).to_dicts()
        ]
        return UserAssertOperationsSummaryOut(
            overall=overall,
            by_public_key=by_public_key,
        )



    async def execute(self, params: GetUserAssetDetailInputParams) -> UserAssetDetailCombinedOut:
        asset_data_from_db = await PostgresUserAssetRepository().get_user_asset_detail(params)
        if asset_data_from_db is None:
            raise UserAssetAddressNotFoundError({'ticker_id': params.ticker_id})
        
        return self._calculate_operations_summary(asset_data_from_db)

