import datetime

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers

@workflow.defn
class UpsertTicketsWorkflow:

    @workflow.run
    async def run(self) -> None:
        return await workflow.execute_activity(
            upsert_tickers,
            schedule_to_close_timeout=datetime.timedelta(minutes=10),
        )
