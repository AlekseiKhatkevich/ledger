from typing import TypedDict, NewType, NotRequired


class CoinsListResponseElement(TypedDict):
    id: str
    symbol: str
    name: str


type CoinsListResponse = list[CoinsListResponseElement]




UnixTimestamp = NewType('UnixTimestamp', int)

class CryptoPriceResponseElement(TypedDict):
    usd: NotRequired[float]
    last_updated_at: UnixTimestamp


type CryptoPriceResponse = dict[str, CryptoPriceResponseElement]
