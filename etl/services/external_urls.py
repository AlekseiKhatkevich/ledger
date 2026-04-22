from functools import cache

import httpx

from config import settings
from custom_types import CoinsListResponse


@cache
class ExternalUrlsService:

    @staticmethod
    async def get_coins_list() -> CoinsListResponse:
        async with httpx.AsyncClient() as client:
            resp = await client.get(settings.EXTERNAL_URL_COINS_LIST.encoded_string())
            return resp.json()