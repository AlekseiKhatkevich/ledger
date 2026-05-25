import datetime
from typing import AsyncGenerator
from typing import TYPE_CHECKING

import httpx
import ijson
import msgspec
from temporalio import exceptions as temporal_exc

from config import settings
from repositories.serializers import CoinGeckoSimplePriceElementDataSchema

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

    @staticmethod
    def _check_status_code(response: httpx.Response) -> None:
        """Set following retry to a value form a header Retry-After"""
        match response.status_code:
            case httpx.codes.TOO_MANY_REQUESTS:
                retry_after_value = int(response.headers['Retry-After'])
                raise temporal_exc.ApplicationError(
                    f"429 from CoinGeco. Retry after header {retry_after_value}",
                    type="CoinGecko_429",
                    non_retryable=False,
                    next_retry_delay=datetime.timedelta(seconds=retry_after_value),
                )
            case _:
                response.raise_for_status()

    async def get_prices(
            self,
            ticker_names: set[str],
    ) -> dict[str, CoinGeckoSimplePriceElementDataSchema]:
        """Get list of prices from coingecko"""
        params = {
            'symbols': ','.join(ticker_names),
            'vs_currencies': 'usd',
            'include_last_updated_at': True,
        }
        async with httpx.AsyncClient(timeout=5.0,) as client:
            response = await client.get(
                settings.EXTERNAL_URL_ASSET_PRICES.encoded_string(),
                params=params,
            )
            self._check_status_code(response)
            data: CryptoPriceResponse = response.json()

        return msgspec.convert(
            {k.upper(): v for k, v in data.items()},
            dict[str, CoinGeckoSimplePriceElementDataSchema],
            strict=False,  # to convert unix timestamp into datetime
        )
