from temporalio import activity

from repositories.database.domain.ledger import LedgerPriceOutTemporalDTO
from usecases.update_prices import UpdatePricesUseCase
from usecases.upsert_tickers import UpsertCryptoTickersInDbUseCase


@activity.defn
async def upsert_tickers(batch_size: int = 1000) -> None:
    return await UpsertCryptoTickersInDbUseCase(batch_size=batch_size).execute()

@activity.defn
async def get_prices_batch(
        tickers: set[str],
        batch_size: int,
) -> list[LedgerPriceOutTemporalDTO]:
    return await UpdatePricesUseCase().execute(tickers, batch_size)
