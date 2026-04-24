import anyio
import asyncstdlib

from repositories.database.ledger import LedgerDbRepository
from repositories.external_urls import ExternalUrlsRepository


class UpsertCryptoTickersInDbUseCase:

    def __init__(self) -> None:
        self.batch_size = 1000
        self.ext_url_service = ExternalUrlsRepository()
        self.db_repository = LedgerDbRepository()


    async def execute(self) -> None:
        async for batch in asyncstdlib.batched(
                self.ext_url_service.get_coins_list(),
                self.batch_size,
        ):
                await self.db_repository.upsert_tickers(frozenset(batch))


if __name__ == '__main__':
    anyio.run(UpsertCryptoTickersInDbUseCase().execute)
