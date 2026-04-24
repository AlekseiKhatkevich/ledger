import datetime

from temporalio import workflow
from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleSpec,
    ScheduleIntervalSpec,
    ScheduleState,
)

from schedules.base import TemporalSchedule

with workflow.unsafe.imports_passed_through():
    from workflows.ledger import UpsertTicketsWorkflow
    from workers.task_queues import LEDGER_TASK_QUEUE


# noinspection PyTypeChecker
ledger_upsert_tickers_hourly = TemporalSchedule(
    id='ledger_upsert_tickers_hourly',
    schedule=Schedule(
        action=ScheduleActionStartWorkflow(
            UpsertTicketsWorkflow.run,
            id='ledger_upsert_tickers_hourly',
            task_queue=LEDGER_TASK_QUEUE,
            ),
            spec=ScheduleSpec(intervals=[ScheduleIntervalSpec(every=datetime.timedelta(hours=1))]),
            state=ScheduleState(note='Hourly Ledger tickers update from Coingecko'),
            ),
    workflow=UpsertTicketsWorkflow,
)


schedules = (ledger_upsert_tickers_hourly, )