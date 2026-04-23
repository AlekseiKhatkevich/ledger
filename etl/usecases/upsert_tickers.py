import asyncstdlib

from repositories.external_urls import ExternalUrlsRepository
from db.postgres.connection import ledger_db


class UpsertCryptoTickersInDbUseCase:

    def __init__(self):
        self.batch_size = 1000
        self.ext_url_service = ExternalUrlsRepository()


    async def execute(self) -> None:
        async for batch in asyncstdlib.batched(
                self.ext_url_service.get_coins_list(),
                self.batch_size,
        ):
                pass

