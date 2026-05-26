import datetime
from functools import singledispatchmethod
from typing import NoReturn

import httpx
import temporalio.exceptions as temporal_exc

from repositories.database.domain.ledger import LedgerPricesFromDB, LedgerPriceOutTemporalDTO
from repositories.database.ledger import LedgerDbRepository
from repositories.external_urls import ExternalUrlsRepository
from repositories.serializers import CoinGeckoSimplePriceElementDataSchema


class UpdatePricesUseCase:
    def __init__(self):
        self.ext_url_service = ExternalUrlsRepository()
        self.db_repository = LedgerDbRepository()

    async def _finalize(self) -> None:
        await self.db_repository.pg_advisory_unlock_all()

    @staticmethod
    def _merge_coingecko_data(
            tickers_from_db: list[LedgerPricesFromDB],
            response_data: dict[str, CoinGeckoSimplePriceElementDataSchema],
    ) -> list[LedgerPricesFromDB]:
        db_prices_dict = {p.name: p for p in tickers_from_db}

        for name, resp_data in response_data.items():
            if resp_data.usd is not None:
                db_price = db_prices_dict[name]
                if db_price.updated_at < resp_data.last_updated_at:
                    db_price.price = resp_data.usd
                    db_price.updated_at = resp_data.last_updated_at

        return tickers_from_db

    @singledispatchmethod
    @staticmethod
    def _handle_api_exceptions(err: httpx.HTTPError ) -> NoReturn:
        raise err

    # noinspection PyNestedDecorators
    @_handle_api_exceptions.register
    @staticmethod
    def _(err: httpx.HTTPStatusError) -> NoReturn:
        """Set following retry to a value form a header Retry-After"""
        match err.response.status_code:
            case httpx.codes.TOO_MANY_REQUESTS:
                retry_after_value = int(err.response.headers['Retry-After'])
                raise temporal_exc.ApplicationError(
                    f"429 from CoinGeco. Retry-After header value -- {retry_after_value}",
                    type="CoinGecko_429",
                    non_retryable=False,
                    next_retry_delay=datetime.timedelta(seconds=retry_after_value),
                )
            case _:
                raise err

    async def execute(self, ticker_names: set[str], batch_size: int) -> list[LedgerPriceOutTemporalDTO]:
        tickers_for_update_from_db = await self.db_repository.get_prices_batch(
            ticker_names,
            batch_size,
        )
        all_ticker_names = {ticker.name for ticker in tickers_for_update_from_db}

        try:
            price_response_data = await self.ext_url_service.get_prices(all_ticker_names)
        except httpx.HTTPError as err:
            await self._finalize()
            self._handle_api_exceptions(err)

        updated_tickers = self._merge_coingecko_data(tickers_for_update_from_db, price_response_data)
        #  filter out ticker prices that are not in DB yet with zero prices
        tickers_for_update_in_db = [t for t in updated_tickers if (t.price or t.id is not None)]
        final_ticker_prices_from_db = await self.db_repository.update_prices(
            tickers_for_update_in_db,
            ticker_names,
        )
        await self._finalize()
        return [
            LedgerPriceOutTemporalDTO(price=ftp.price, name=ftp.name)
            for ftp in final_ticker_prices_from_db
        ]
