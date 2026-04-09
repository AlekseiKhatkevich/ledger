import datetime
import decimal
import enum
import uuid
from typing import Annotated

from sqlalchemy import BIGINT, Identity, String, ForeignKey, Computed, Index, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import mapped_column, Mapped

from database.postgres.base import Base


class AssetOperationType(enum.StrEnum):
    PURCHASE = 'PURCHASE'
    SELL = 'SELL'


class UserAssetAddress(Base):
    __tablename__ = 'user_asset_addresses'

    id: Mapped[Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True)]]
    public_key: Mapped[str]
    wallet_name: Mapped[str | None]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.wallet_name = })'

class AssetTicker(Base):
    __tablename__ = 'asset_tickers'
    name: Mapped[Annotated[str, mapped_column(String(10), primary_key=True)]]

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.name = })'


class UserAssetOperation(Base):
    __tablename__ = 'user_asset_operations'

    id: Mapped[Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True)]]
    time: Mapped[datetime.datetime]
    type: Mapped[Annotated[enum.Enum, mapped_column(ENUM(AssetOperationType, name='asset_operation_type'))]]
    user_asset_id: Mapped[
        Annotated[int, mapped_column(ForeignKey('user_assets.id', ondelete='CASCADE'))]
    ] # index
    quantity: Mapped[decimal.Decimal]
    unit_price: Mapped[decimal.Decimal]
    summ: Mapped[Annotated[decimal.Decimal, mapped_column(Computed('unit_price * quantity'))]]
    address: Mapped[
        Annotated[int, mapped_column(ForeignKey('user_asset_address.id', ondelete='RESTRICT'))]
    ]

    # parent = relationship("Parent", back_populates="children")

    __table_args__ = (
        Index('ix_user_asset_id', 'user_asset_id'),
        CheckConstraint('quantity > 0', name='asset_qty_gt_0'),
        CheckConstraint('unit+price > 0', name='unit_price_gt_0'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.user_asset_id = })'

class UserAsset(Base):
    __tablename__ = 'user_assets'

    id: Mapped[Annotated[int, mapped_column(BIGINT, Identity(always=True), primary_key=True)]]
    name: Mapped[str]
    ticker: Mapped[Annotated[str, mapped_column(ForeignKey('asset_tickers.name', ondelete='RESTRICT'))]]
    user_id: Mapped[uuid.UUID]

    __table_args__ = (
        UniqueConstraint('user_id', 'ticker', ),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.name})'

    # children = relationship(
    #     "Child",
    #     back_populates="parent",
    #     cascade="all, delete",
    #     passive_deletes=True,
    # )

    # todo
    # @hybrid property

