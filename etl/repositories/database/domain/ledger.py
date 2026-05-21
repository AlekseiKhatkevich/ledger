import dataclasses
import datetime
import decimal


@dataclasses.dataclass
class LedgerPricesFromDBForUpdate:
    name: str
    price: decimal.Decimal
    updated_at: datetime.datetime
    id: int | None = None
