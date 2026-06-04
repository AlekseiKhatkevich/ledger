import asyncio
from typing import Coroutine, Any


async def wrap_create_task(
        coro: Coroutine,
        schedule_now: bool = False,
        **kwargs: dict[str, Any],
) -> asyncio.Task:
    task = asyncio.create_task(coro, **kwargs)
    # Local container for one task, lives until task completes
    _tasks_container: set[asyncio.Task] = {task}
    task.add_done_callback(_tasks_container.discard)
    if schedule_now:
        await asyncio.sleep(0)
    return task
