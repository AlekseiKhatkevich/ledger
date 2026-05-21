from typing import AsyncGenerator
from typing import TYPE_CHECKING

import httpx
import ijson

from config import settings
from repositories.database.domain.ledger import LedgerPricesFromDBForUpdate

if TYPE_CHECKING:
    from custom_types import CryptoPriceResponse



class ExternalUrlsRepository:

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

    # todo Retry-After в хедерах, httpx.RequestError
    # https://will-ockmore.github.io/httpx-retries/api/
    @staticmethod
    async def get_prices(tickers_from_db: list[LedgerPricesFromDBForUpdate]) -> CryptoPriceResponse:
        """Get list of prices from coingecko"""
        params = {
            'symbols': ','.join(ticker.name for ticker in tickers_from_db),
            'vs_currencies': 'usd',
            'include_last_updated_at': True,
        }
        async with httpx.AsyncClient(timeout=5.0,) as client:
            response = await client.get(
                settings.EXTERNAL_URL_ASSET_PRICES.encoded_string(),
                params=params,
            )
            response.raise_for_status()
            return response.json()
