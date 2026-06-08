import datetime
import decimal
import uuid
from dataclasses import dataclass, field

import msgspec
from advanced_alchemy import filters as sa_filters
from advanced_alchemy.filters import StatementFilter
from litestar.dto import DTOConfig, MsgspecDTO
from sqlalchemy import Select, Executable

from database.postgres.base import Base
from logic.db_models import AssetOperationType


@dataclass(frozen=True)
class DbCRUDOperationReturnData:
    id: int | None
    asset_exists: bool
    address_exists: bool
    balance: decimal.Decimal
    balance_ok: bool


class UserAssetOperationData(msgspec.Struct):
    time: datetime.datetime
    type: AssetOperationType
    user_id: uuid.UUID
    quantity: decimal.Decimal
    unit_price: decimal.Decimal
    id: int | None
    user_asset_id: int = 0
    address_id: int = 0


    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(
                f"quantity must be > 0, got {self.quantity}"
            )
        if self.unit_price <= 0:
            raise ValueError(
                f"unit_price must be > 0, got {self.unit_price}"
            )


@dataclass(frozen=True)
class UserAssetOperationDetailOut:
    id: int
    type: AssetOperationType
    quantity: decimal.Decimal
    unit_price: decimal.Decimal
    summ: decimal.Decimal
    time: datetime.datetime
    wallet_name: list[str]
    public_key: str


@dataclass(frozen=True)
class UserAssetOperationSummaryGrouped:
    key: str
    type: str
    count: decimal.Decimal
    total_quantity: decimal.Decimal
    total_summ: decimal.Decimal


@dataclass(frozen=True)
class UserAssertOperationsSummaryOut:
    overall: list[UserAssetOperationSummaryGrouped]
    by_public_key: list[UserAssetOperationSummaryGrouped]


class UserAssetOperationDTOIn(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'id', 'user_id'})


class UserAssetOperationDTOOut(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'user_id', })


class UserAssetOperationUpdateDTOIn(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'user_id', })


@dataclass(frozen=True)
class UserAssetOperationsFilter:
    time__gte: datetime.datetime | None = None
    time__lte: datetime.datetime | None = None
    op_id: list[int] | None = None
    op_type: tuple[AssetOperationType, ...] = field(default_factory=lambda: tuple(AssetOperationType))
    address_id: list[int] | None = None

    def __post_init__(self) -> None:
        if self.time__gte and self.time__lte and self.time__gte > self.time__lte:
            raise ValueError('time__gte field should be lighter then time__lte field')

    @property
    def alchemy_filters(self) -> list[StatementFilter]:
        return [
            sa_filters.BeforeAfter(field_name='time', before=self.time__lte, after=self.time__gte, ),
            sa_filters.CollectionFilter(field_name='id', values=self.op_id),
            sa_filters.CollectionFilter(field_name='address_id', values=self.address_id),
            sa_filters.CollectionFilter(field_name='type', values=self.op_type),
        ]
