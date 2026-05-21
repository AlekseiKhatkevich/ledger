import decimal

from custom_types import CryptoPriceResponse
from repositories.database.domain.ledger import LedgerPricesFromDBForUpdate
from repositories.database.ledger import LedgerDbRepository
from repositories.external_urls import ExternalUrlsRepository
from repositories.serializers import CoinGeckoSimplePriceElementDataSchema


class UpdatePricesUseCase:
    def __init__(self):
        self.ext_url_service = ExternalUrlsRepository()
        self.db_repository = LedgerDbRepository()

    # todo финализация в случае 429го респонса
    async def _finalize(self) -> None:
        await self.db_repository.pg_advisory_unlock_all()

    @staticmethod
    def _merge_coingecko_data(
            tickers_from_db: list[LedgerPricesFromDBForUpdate],
            response_data: dict[str, CoinGeckoSimplePriceElementDataSchema],
    ) -> list[LedgerPricesFromDBForUpdate]:
        db_prices_dict = {p.name: p for p in tickers_from_db}

        for name, resp_data in response_data:
            try:
                db_price = db_prices_dict[name]
            except KeyError:  # does not have price in DB yet
                tickers_from_db.append(
                    LedgerPricesFromDBForUpdate(
                        name=name,
                        price=resp_data.usd,
                        updated_at=resp_data.last_updated_at,
                    )
                )
            else:
                db_price.price = resp_data.usd
                db_price.updated_at = resp_data.last_updated_at

        return tickers_from_db


    async def execute(self, tickers: tuple[str, ...], batch_size: int):
        tickers_for_update_from_db = await self.db_repository.get_prices_batch(
            tickers,
            batch_size,
        )
        #  we need to send all tickers even if some of them are not in DB yet ...
        all_tickers = {ticker.name for ticker in tickers_for_update_from_db} | set(tickers)
        price_response_data = await self.ext_url_service.get_prices(all_tickers)
        updated_tickers = self._merge_coingecko_data(tickers_for_update_from_db, price_response_data)

        return  updated_tickers

