import asyncio
from typing import Coroutine


async def wrap_create_task(
        coro: Coroutine,
        schedule_now: bool = False,
) -> asyncio.Task:
    task = asyncio.create_task(coro)
    # Local container for one task, lives until task completes
    _tasks_container: set[asyncio.Task] = {task}
    task.add_done_callback(_tasks_container.discard)
    if schedule_now:
        await asyncio.sleep(0)
    return task
