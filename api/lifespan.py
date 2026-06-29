import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from litestar import Litestar

from aux.openbao.client import openbao_client
from config import settings
from database.postgres.connection import db
from interservice.worker import Node


def set_settings(app:Litestar) -> None:
    app.state.settings = settings


@asynccontextmanager
async def nng_node(app:Litestar) -> AsyncGenerator[None]:
    n = Node(survey=False)
    app.state.nng_node = n

    task = asyncio.create_task(n.run())

    try:
        yield
    finally:
        await n.stop()
        task.cancel()


on_startup = [set_settings, openbao_client.unseal]

on_shutdown = [db.close]

lifespan = [nng_node, ]