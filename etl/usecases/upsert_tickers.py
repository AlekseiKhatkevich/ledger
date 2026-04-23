import asyncstdlib

from db.postgres.models import LedgerModels
from repositories.external_urls import ExternalUrlsRepository


class UpsertCryptoTickersInDbUseCase:

    def __init__(self):
        self.batch_size = 1000
        self.ext_url_service = ExternalUrlsRepository()
        # self.ledger_models = LedgerModels()


    async def execute(self) -> None:
        async for batch in asyncstdlib.batched(
                self.ext_url_service.get_coins_list(),
                self.batch_size,
        ):
                pass

