import datetime

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers

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
    async def run(self, tickers: tuple[str]) -> dict:
        pass
