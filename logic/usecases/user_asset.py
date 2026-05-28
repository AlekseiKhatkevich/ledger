import uuid
from decimal import Decimal

import polars as pl
from temporalio.client import WorkflowHandle

from api.user_asset_operations.domain import (
    UserAssertOperationsSummaryOut,
    UserAssetOperationSummaryGrouped,
)
from api.user_assets.domain import AssetPublicKeyDetailOut, UserAssetPriceSimple
from api.user_assets.domain import (
    UserAssetData,
    UserAssetAggregatedPage,
    GetUserAssetDetailInputParams,
    UserAssetDetailCombinedOut,
)
from aux.temporal.client import get_client
from aux.temporal.domain import UpdatePricesWorkflowParams
from aux.temporal.workflows import TEMPORAL_UPDATE_PRICES_FLOW
from constants import LEDGER_TASK_QUEUE
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import AssetOperationType
from logic.exceptions import UserAssetNotFoundError


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

    def __init__(self) -> None:
        self._temporal_handle = None

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
                public_key=row['public_key'],
                in_tock=(in_tock := row['in_tock']),
                market_value=in_tock * price if price is not None else None,
            )
            for row in details.to_dicts()
        ]

    @staticmethod
    async def _check_if_price_outdated(
            asset_data_from_db: UserAssetDetailCombinedOut,
    ) -> WorkflowHandle | None:
        if asset_data_from_db.user_asset.outdated:
            temporal_client = await get_client()
            workflow_handle = await temporal_client.start_workflow(
                TEMPORAL_UPDATE_PRICES_FLOW,
                UpdatePricesWorkflowParams(
                    tickers={asset_data_from_db.user_asset.ticker_id,},
                ),
                id=f'{TEMPORAL_UPDATE_PRICES_FLOW}-{uuid.uuid4()}',
                task_queue=LEDGER_TASK_QUEUE,
            )
            return workflow_handle

    async def get_price_after_update_in_temporal(self) -> list[UserAssetPriceSimple] | None:
        #  if we actually sent a request to temporal
        if self._temporal_handle is not None:
            update_prices_result = await self._temporal_handle.result()
            return [UserAssetPriceSimple(**upr) for upr in update_prices_result]

    async def execute(self, params: GetUserAssetDetailInputParams) -> UserAssetDetailCombinedOut:
        asset_data_from_db = await PostgresUserAssetRepository().get_user_asset_detail(params)
        if asset_data_from_db is None:
            raise UserAssetNotFoundError({'ticker_id': params.ticker_id})

        self._temporal_handle = await self._check_if_price_outdated(asset_data_from_db)

        asset_data_from_db.operations_summary = self._calculate_operations_summary(asset_data_from_db)
        asset_data_from_db.public_key_details = self._calculate_public_key_details(asset_data_from_db)

        return asset_data_from_db