import dataclasses
import datetime
import decimal


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
