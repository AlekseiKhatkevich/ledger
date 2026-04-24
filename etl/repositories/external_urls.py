from typing import AsyncGenerator

import httpx
import ijson

from config import settings


class ExternalUrlsRepository:

# todo check etag
    @staticmethod
    async def get_coins_list() -> AsyncGenerator[str]:
        """Get list of crypto symbols (tickers). Seems like it might contain duplicates"""
        async with httpx.AsyncClient() as client:
            async with client.stream('GET', settings.EXTERNAL_URL_COINS_LIST.encoded_string()) as resp:
                resp.raise_for_status()
                f = ijson.from_iter(resp.aiter_bytes())
                objects = ijson.items(f, 'item.symbol')
                async for symbol in objects:
                    yield symbol
