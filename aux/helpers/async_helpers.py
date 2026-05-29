import asyncio
from typing import Coroutine


async def wrap_create_task(
        coro: Coroutine,
        tasks_container: set[asyncio.Task],
        schedule_now: bool = False,
) -> asyncio.Task:
    task = asyncio.create_task(coro)
    tasks_container.add(task)
    task.add_done_callback(tasks_container.discard)
    if schedule_now:
        await asyncio.sleep(0)
    return task