import contextlib
import datetime
from concurrent.futures import ThreadPoolExecutor, Executor
from dataclasses import dataclass, field, fields
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
    activity_executor: Executor = field(default_factory=lambda: ThreadPoolExecutor(max_workers=200))
    workflow_task_executor: Executor = field(default_factory=lambda: ThreadPoolExecutor(max_workers=24))
    max_concurrent_activities: int = 200
    max_concurrent_workflow_tasks : int= 24
    max_cached_workflows: int = 500
    max_concurrent_activity_task_polls: int = 8
    max_concurrent_workflow_task_polls: int = 8
    nonsticky_to_sticky_poll_ratio: float = 0.1
    graceful_shutdown_timeout: datetime.timedelta = datetime.timedelta(seconds=60)


async def start_worker(worker_data: WorkerData, create_schedules: bool=False) -> None:
    client = await Client.connect(settings.TEMPORAL_ADDRESS)

    worker = Worker(
        client,
        **{f.name: getattr(worker_data, f.name) for f in fields(WorkerData)}
    )

    if create_schedules:
        for schedule in schedules:
            if schedule.workflow in worker.config()['workflows']:
                with contextlib.suppress(ScheduleAlreadyRunningError):
                    await client.create_schedule(*schedule)

    await worker.run()