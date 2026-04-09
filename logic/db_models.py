import datetime
import decimal
import enum
import uuid
from typing import Annotated

from sqlalchemy import BIGINT, Identity, String, ForeignKey, Computed
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import mapped_column, Mapped

from database.postgres.base import Base


class AssetOperationType(enum.StrEnum):
    PURCHASE = 'PURCHASE'
    SELL = 'SELL'


# class UserAssetAddress(Base):
#     pass
#
# class Ticker(Base):
#     pass


class UserAssetOperation(Base):
    __tablename__ = 'user_asset_operations'

    id: Mapped[Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True)]]
    time: Mapped[datetime.datetime]
    type: Mapped[Annotated[enum.Enum, mapped_column(ENUM(AssetOperationType, name='asset_operation_type'))]]
    user_asset_id: Mapped[
        Annotated[int, mapped_column(ForeignKey('user_assets.id', ondelete='CASCADE'))]
    ]
    quantity: Mapped[decimal.Decimal]
    unit_price: Mapped[decimal.Decimal]
    summ: Mapped[Annotated[decimal.Decimal, mapped_column(Computed('unit_price * quantity'))]]

    # parent = relationship("Parent", back_populates="children")

class UserAsset(Base):
    __tablename__ = 'user_assets'

    id: Mapped[Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True)]]
    name: Mapped[str]
    ticker: Mapped[Annotated[str, mapped_column(String(10))]]
    user_id: Mapped[uuid.UUID]  # ticker + user unique together

    # children = relationship(
    #     "Child",
    #     back_populates="parent",
    #     cascade="all, delete",
    #     passive_deletes=True,
    # )


