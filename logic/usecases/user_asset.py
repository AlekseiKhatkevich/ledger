import dataclasses
import uuid
from decimal import Decimal

import polars as pl

from api.user_asset_operations.domain import UserAssertOperationsSummaryOut, UserAssetOperationSummaryGrouped
from api.user_assets.domain import AssetPublicKeyDetailOut
from api.user_assets.domain import (
    UserAssetData,
    UserAssetAggregatedPage,
    GetUserAssetDetailInputParams,
    UserAssetDetailCombinedOut,
)
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import AssetOperationType
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

    @staticmethod
    def _calculate_operations_summary(
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

    @staticmethod
    def _calculate_public_key_details(
        asset_data_from_db: UserAssetDetailCombinedOut,
    ) -> list[AssetPublicKeyDetailOut]:
        price = asset_data_from_db.user_asset.price
        ticker_id = asset_data_from_db.user_asset.ticker_id

        df = pl.DataFrame(
            asset_data_from_db.operations,
            schema_overrides={
                'quantity': pl.Decimal(scale=10),
                'unit_price': pl.Decimal(scale=10),
                'summ': pl.Decimal(scale=10),
            },
        )
        pivot_df = df.pivot(
            index='public_key',
            on='type',
            values='quantity',
            aggregate_function='sum',
        ).fill_null(Decimal(0))

        details = pivot_df.with_columns(
            pl.max_horizontal(
                pl.col(AssetOperationType.PURCHASE) - pl.col(AssetOperationType.SELL),
                pl.lit(Decimal(0)),
            ).alias('in_tock'),
        )

        return [
            AssetPublicKeyDetailOut(
                asset_id=ticker_id,
                public_key=row['public_key'],
                in_tock=(in_tock := row['in_tock']),
                market_value=in_tock * price if price is not None else None,
            )
            for row in details.to_dicts()
        ]

    async def execute(self, params: 'GetUserAssetDetailInputParams') -> UserAssertOperationsSummaryOut:
        asset_data_from_db = await PostgresUserAssetRepository().get_user_asset_detail(params)
        if asset_data_from_db is None:
            raise UserAssetAddressNotFoundError({'ticker_id': params.ticker_id})
        
        return self._calculate_public_key_details(asset_data_from_db)