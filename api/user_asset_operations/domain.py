import datetime
import decimal
import uuid
from dataclasses import dataclass

import msgspec
from litestar.dto import DTOConfig, MsgspecDTO

from logic.db_models import AssetOperationType


@dataclass(frozen=True)
class DbCRUDOperationReturnData:
    id: int | None
    asset_exists: bool
    address_exists: bool
    # balance: decimal.Decimal
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


class UserAssetOperationDTOIn(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'id', 'user_id'})


class UserAssetOperationDTOOut(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'user_id', })


class UserAssetOperationUpdateDTOIn(MsgspecDTO[UserAssetOperationData]):
    config = DTOConfig(exclude={'user_id', })