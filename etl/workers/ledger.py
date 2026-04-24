import asyncio
import contextlib
import datetime
from collections.abc import Iterator
from dataclasses import dataclass

import temporalio
from temporalio import workflow
from temporalio.client import Client
from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
    ScheduleState,
)
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    from activities.ledger import upsert_tickers
    from workflows.ledger import UpsertTicketsWorkflow
    from config import settings
    from workers.task_queues import LEDGER_TASK_QUEUE


@dataclass
class TemporalSchedule:
    id: str
    schedule: Schedule

    def __iter__(self) -> Iterator:
        return iter((self.id, self. schedule))

ledger_upsert_tickers_hourly = TemporalSchedule(
    'ledger_upsert_tickers_hourly',
    Schedule(
        action=ScheduleActionStartWorkflow(
            UpsertTicketsWorkflow.run,
            id='ledger_upsert_tickers_hourly',
            task_queue=LEDGER_TASK_QUEUE,
            ),
            spec=ScheduleSpec(intervals=[ScheduleIntervalSpec(every=datetime.timedelta(hours=1))]),
            state=ScheduleState(note='Hourly Ledger tickers update from Coingecko'),
            )
)

schedules = (ledger_upsert_tickers_hourly, )

async def main() -> None:
    client = await Client.connect(settings.TEMPORAL_ADDRESS)

    for schedule in schedules:
        with contextlib.suppress(temporalio.client.ScheduleAlreadyRunningError):
            await client.create_schedule(*schedule)

    worker = Worker(
        client,
        task_queue=LEDGER_TASK_QUEUE,
        workflows=[UpsertTicketsWorkflow, ],
        activities=[upsert_tickers, ],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
