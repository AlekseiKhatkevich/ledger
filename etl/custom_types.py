from typing import TypedDict


class CoinsListResponseElement(TypedDict):
    id: str
    symbol: str
    name: str


type CoinsListResponse = list[CoinsListResponseElement]