import contextlib
from dataclasses import dataclass, asdict
from typing import Callable

from temporalio.client import Client, ScheduleAlreadyRunningError
from temporalio.worker import Worker

from config import settings
from schedules import schedules


@dataclass
class WorkerData:
    task_queue: str
    workflows: list[object]
    activities: list[Callable]


async def start_worker(worker_data: WorkerData) -> None:
    client = await Client.connect(settings.TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        **asdict(worker_data),
    )

    for schedule in schedules:
        if schedule.workflow in worker.config()['workflows']:
            with contextlib.suppress(ScheduleAlreadyRunningError):
                await client.create_schedule(*schedule)

    await worker.run()