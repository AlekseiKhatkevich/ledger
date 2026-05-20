import dataclasses
import datetime
import decimal


@dataclasses.dataclass
class LedgerPricesFromDBForUpdate:
    id: int
    name: str
    price: decimal.Decimal
    updated_at: datetime.timedelta
    num_usages: int | None

