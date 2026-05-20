import datetime

# https://docs.coingecko.com/reference/simple-price#note
LEDGER_PRICES_BATCH_SIZE: int = 515
LEDGER_PRICES_PRICE_TIMEOUT: datetime.timedelta = datetime.timedelta(minutes=5)
LEDGER_PRICES_LOCK_NAMESPACE: int = 14