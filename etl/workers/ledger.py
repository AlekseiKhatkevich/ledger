import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio import workflow


with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers
    from workflows.ledger import UpsertTicketsWorkflow
    from config import settings
    from workers.task_queues import LEDGER_TASK_QUEUE


async def main() -> None:
    client = await Client.connect(settings.TEMPORAL_ADDRESS)
    worker = Worker(
        client,
        task_queue=LEDGER_TASK_QUEUE,
        workflows=[UpsertTicketsWorkflow, ],
        activities=[upsert_tickers, ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
