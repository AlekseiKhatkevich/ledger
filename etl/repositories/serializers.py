import datetime
import decimal

import msgspec


class CoinGeckoSimplePriceElementDataSchema(msgspec.Struct):
    last_updated_at: datetime.datetime
    usd: decimal.Decimal | None = None
