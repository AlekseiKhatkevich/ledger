import asyncio

import pytest

from aux.helpers.async_helpers import wrap_create_task


async def _coro(container):
    container.append(1)

@pytest.mark.parametrize('schedule_now', [False, True])
async def test_wrap_create_task(schedule_now):
    _mutate_me = []
    task = await wrap_create_task(_coro(_mutate_me), schedule_now=schedule_now)
    await asyncio.sleep(0.05)

    assert 1 in _mutate_me
    assert task.done()
    assert task not in asyncio.all_tasks()