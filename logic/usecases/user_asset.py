import asyncio
import datetime
import uuid
from decimal import Decimal

import polars as pl

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
from aux.helpers.async_helpers import wrap_create_task
from aux.temporal.client import get_client
from aux.temporal.domain import UpdatePricesWorkflowParams
from aux.temporal.workflows import TEMPORAL_UPDATE_PRICES_FLOW
from constants import LEDGER_TASK_QUEUE
from database.postgres.repositories.asset_ticker_price import PostgresAssetTickerPriceRepository
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository
from logic.db_models import AssetOperationType
from logic.exceptions import UserAssetNotFoundError


class UserAssetUpsertUseCase:

    @staticmethod
    async def execute(data: UserAssetData) -> int | None:
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

    def __init__(self, price_update_interval: datetime.timedelta | None = None) -> None:
        self.result_queue = asyncio.Queue()
        self._user_asset_repo = PostgresUserAssetRepository()
        self._ticker_price_repo = PostgresAssetTickerPriceRepository()
        self.price_update_interval = price_update_interval
        self.final_event = asyncio.Event()

    @staticmethod
    def _calculate_operations_summary(
            asset_data_from_db: UserAssetDetailCombinedOut,
    ) -> UserAssertOperationsSummaryOut:
        df = pl.DataFrame(
            asset_data_from_db.operations,
            schema_overrides={
                'quantity': pl.Decimal(scale=10),
                'unit_price': pl.Decimal(scale=10),
                'summ': pl.Decimal(scale=10),
            },
        )
        agg_exprs = [
            pl.len().alias('count'),
            pl.sum('quantity').alias('total_quantity'),
            pl.sum('summ').alias('total_summ'),
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

    async def update_price_periodically(self, asset_data_from_db: UserAssetDetailCombinedOut) -> None:
        while not self.final_event.is_set():
            await asyncio.sleep(self.price_update_interval.total_seconds())
            price_data_from_db = await self._ticker_price_repo.get_prices(
                {asset_data_from_db.user_asset.ticker_id, }
            )
            outdated_tickers = {pd.name for pd in price_data_from_db if pd.outdated}
            if outdated_tickers:
                await wrap_create_task(self._update_prices_from_coingecko(outdated_tickers),)
            return_data = [UserAssetPriceSimple(name=pd.name, price=pd.price) for pd in price_data_from_db]
            await self.result_queue.put(return_data)


    async def _update_prices_from_coingecko(
            self,
            ticker_names:set[str],
    ) -> list[UserAssetPriceSimple]:
        temporal_client = await get_client()
        result = await temporal_client.execute_workflow(
            TEMPORAL_UPDATE_PRICES_FLOW,
            UpdatePricesWorkflowParams(tickers=ticker_names),
            id=f'{TEMPORAL_UPDATE_PRICES_FLOW}-{uuid.uuid4()}',
            task_queue=LEDGER_TASK_QUEUE,
        )
        updated_price_data = [UserAssetPriceSimple(**upr) for upr in result]
        await self.result_queue.put(updated_price_data)
        return updated_price_data


    async def _check_if_price_outdated(
            self,
            asset_data_from_db: UserAssetDetailCombinedOut,
    ) -> list[UserAssetPriceSimple] | None:
        if asset_data_from_db.user_asset.outdated:
            tickers = {asset_data_from_db.user_asset.ticker_id}
            return await self._update_prices_from_coingecko(tickers)

    async def execute(self, params: GetUserAssetDetailInputParams) -> UserAssetDetailCombinedOut:
        asset_data_from_db = await self._user_asset_repo.get_user_asset_detail(params)
        if asset_data_from_db is None:
            raise UserAssetNotFoundError({'ticker_id': params.ticker_id})

        await wrap_create_task(
            self._check_if_price_outdated(asset_data_from_db),
            True,
        )
        if self.price_update_interval is not None:
            await wrap_create_task(
                self.update_price_periodically(asset_data_from_db),
                True,
            )

        asset_data_from_db.operations_summary = self._calculate_operations_summary(asset_data_from_db)
        asset_data_from_db.public_key_details = self._calculate_public_key_details(asset_data_from_db)
        await self.result_queue.put(asset_data_from_db)

        return asset_data_from_db