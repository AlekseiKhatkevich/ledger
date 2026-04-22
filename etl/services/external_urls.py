from functools import cache
from typing import AsyncGenerator

import httpx
import ijson

from config import settings


@cache
class ExternalUrlsService:

    @staticmethod
    async def get_coins_list() -> AsyncGenerator[str]:
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', settings.EXTERNAL_URL_COINS_LIST.encoded_string()) as resp:
                resp.raise_for_status()
                f = ijson.from_iter(resp.aiter_bytes())
                objects = ijson.items(f, 'item.symbol')
                symbols = (o async for o in objects)
                async for symbol in symbols:
                    yield symbol
