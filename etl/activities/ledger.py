from temporalio import activity

from usecases.update_prices import UpdatePricesUseCase
from usecases.upsert_tickers import UpsertCryptoTickersInDbUseCase
import constants


@activity.defn
async def upsert_tickers(batch_size: int = 1000) -> None:
    return await UpsertCryptoTickersInDbUseCase(batch_size=batch_size).execute()

# todo retry 429, etc, timeout
@activity.defn
async def get_prices_batch(
        tickers: tuple[str, ...],
        batch_size: int = constants.LEDGER_PRICES_BATCH_SIZE,
):
    await UpdatePricesUseCase().execute(tickers, batch_size)
