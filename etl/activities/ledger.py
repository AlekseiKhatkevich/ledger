from temporalio import activity

from usecases.upsert_tickers import UpsertCryptoTickersInDbUseCase


@activity.defn
async def upsert_tickers(batch_size: int = 1000) -> None:
    return await UpsertCryptoTickersInDbUseCase(batch_size=batch_size).execute()
