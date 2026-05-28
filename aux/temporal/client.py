from functools import cache

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from config import settings

@cache
async def get_client() -> Client:
    return await Client.connect(
        settings.TEMPORAL_ADDRESS,
        data_converter=pydantic_data_converter,
    )
