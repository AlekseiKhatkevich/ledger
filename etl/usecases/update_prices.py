from custom_types import CryptoPriceResponse
from repositories.database.domain.ledger import LedgerPricesFromDBForUpdate
from repositories.database.ledger import LedgerDbRepository
from repositories.external_urls import ExternalUrlsRepository


class UpdatePricesUseCase:
    def __init__(self):
        self.ext_url_service = ExternalUrlsRepository()
        self.db_repository = LedgerDbRepository()

    def _merge_coingecko_data(
            self,
            tickers_from_db: list[LedgerPricesFromDBForUpdate],
            response_data: CryptoPriceResponse,
    ):

    async def execute(self, tickers: tuple[str, ...], batch_size: int):
        tickers_for_update_from_db = await self.db_repository.get_prices_batch(
            tickers,
            batch_size,
        )
        price_response_data = await self.ext_url_service.get_prices(tickers_for_update_from_db)
