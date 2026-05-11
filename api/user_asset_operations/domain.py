import datetime
import decimal
import uuid

import msgspec
from litestar.dto import DTOConfig, MsgspecDTO

from logic.db_models import AssetOperationType


class UserAssetOperationData(msgspec.Struct):
    time: datetime.datetime
    type: AssetOperationType
    user_id: uuid.UUID
    quantity: decimal.Decimal
    unit_price: decimal.Decimal
    user_asset_id: int = 0
    address_id: int = 0
    id: int | None = None

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