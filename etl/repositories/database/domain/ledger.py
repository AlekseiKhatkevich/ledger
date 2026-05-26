import dataclasses
import datetime
import decimal

import constants


@dataclasses.dataclass
class LedgerPricesFromDB:
    name: str
    price: decimal.Decimal
    updated_at: datetime.datetime
    id: int | None = None


@dataclasses.dataclass
class LedgerPriceOutTemporalDTO:
    name: str
    price: decimal.Decimal


@dataclasses.dataclass
class UpdatePricesWorkflowParams:
    tickers: set[str]
    batch_size: int = constants.LEDGER_PRICES_BATCH_SIZE
