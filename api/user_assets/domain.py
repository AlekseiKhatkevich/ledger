import datetime
import decimal
import uuid
from dataclasses import dataclass, field
from typing import Annotated

import msgspec
from litestar.dto import DTOConfig, MsgspecDTO

from api.user_asset_operations.domain import UserAssetOperationDetailOut, UserAssertOperationsSummaryOut, \
    UserAssetOperationsFilter


class UserAssetData(msgspec.Struct):
    name: str
    ticker_id: Annotated[str, msgspec.Meta(max_length=50)]
    user_id: uuid.UUID

    def __post_init__(self) -> None:
        self.ticker_id = self.ticker_id.upper()


class UserAssetDto(MsgspecDTO[UserAssetData]):
    config = DTOConfig(exclude={'user_id', })


@dataclass
class UserAssetAggregatedData:
    """Aggregated per-token stats for a user's portfolio.

    One row per token (user_asset).
    """
    coin_qty_now: decimal.Decimal
    unique_addresses_cnt: int
    purchased_for_usdt: decimal.Decimal
    sold_for_usdt: decimal.Decimal
    num_purchases: int
    num_sells: int
    name: str
    ticker_id: str
    id: int
    wallet_names: list[str] = field(default_factory=list)


@dataclass
class UserAssetAggregatedPage:
    """Paginated response for get_user_asset_aggregates().

    Uses keyset (cursor-based) pagination over ticker_id,
    which leverages the existing (user_id, ticker_id) unique index.
    """
    items: list[UserAssetAggregatedData]
    cursor: str | None  # ticker_id of the last item on this page
    has_more: bool               # whether a next page exists


@dataclass(frozen=True)
class UserAssetDetailOut:
    id: int
    name: str
    ticker_id: str
    price: decimal.Decimal | None
    outdated: bool
    time_when_price_was_update_in_db: datetime.datetime | None
    popularity_rank: int | None


@dataclass(frozen=True)
class AssetPublicKeyDetailOut:
    public_key: str
    in_stock: decimal.Decimal
    market_value: decimal.Decimal | None = None


@dataclass
class UserAssetDetailCombinedOut:
    user_asset: UserAssetDetailOut
    operations: list[UserAssetOperationDetailOut]
    operations_summary: UserAssertOperationsSummaryOut | None = None
    public_key_details: list[AssetPublicKeyDetailOut] | None = None


@dataclass
class GetUserAssetDetailInputParams:
    user_id: uuid.UUID
    ticker_id: str
    with_rank: bool
    op_filter: UserAssetOperationsFilter

    def __post_init__(self) -> None:
        self.ticker_id = self.ticker_id.upper()

@dataclass(frozen=True)
class UserAssetPriceSimple:
    name: str
    price: decimal.Decimal
