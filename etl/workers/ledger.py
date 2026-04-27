import asyncio

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers
    from workflows.ledger import UpsertTicketsWorkflow
    from workers.task_queues import LEDGER_TASK_QUEUE
    from workers.base import start_worker, WorkerData


async def main() -> None:
    worker_data = WorkerData(
        task_queue=LEDGER_TASK_QUEUE,
        workflows=[UpsertTicketsWorkflow, ],
        activities=[upsert_tickers, ],
    )
    await start_worker(worker_data, True)


if __name__ == "__main__":
    asyncio.run(main())
