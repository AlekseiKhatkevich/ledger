import datetime
import decimal
import constants

from temporalio import workflow
from temporalio.common import RetryPolicy

from repositories.database.domain.ledger import LedgerPriceOutTemporalDTO

with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers, get_prices_batch

@workflow.defn
class UpsertTicketsWorkflow:

    @workflow.run
    async def run(self) -> None:
        return await workflow.execute_activity(
            upsert_tickers,
            schedule_to_close_timeout=datetime.timedelta(minutes=55),
            retry_policy=RetryPolicy(
                backoff_coefficient=2,
                initial_interval=datetime.timedelta(seconds=5),
                maximum_interval=datetime.timedelta(seconds=60),
            ),
        )


@workflow.defn
class UpdatePricesWorkflow:

    @workflow.run
    async def run(
            self,
            tickers: set[str],
            batch_size: int = constants.LEDGER_PRICES_BATCH_SIZE,
    ) -> list[LedgerPriceOutTemporalDTO]:
        return await workflow.execute_activity(
            get_prices_batch,
            args=[tickers, batch_size, ],
            schedule_to_close_timeout=datetime.timedelta(seconds=60 * 3),
        )
