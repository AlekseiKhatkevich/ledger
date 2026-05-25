from temporalio import activity

import constants
from usecases.update_prices import UpdatePricesUseCase
from usecases.upsert_tickers import UpsertCryptoTickersInDbUseCase


@activity.defn
async def upsert_tickers(batch_size: int = 1000) -> None:
    return await UpsertCryptoTickersInDbUseCase(batch_size=batch_size).execute()

# todo retry 429, etc, timeout
@activity.defn
async def get_prices_batch(
        tickers: set[str],
        batch_size: int,
):
    return await UpdatePricesUseCase().execute(tickers, batch_size)
