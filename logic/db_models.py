import datetime
import decimal
import enum
import uuid
from typing import Annotated

import sqlalchemy as sa
from sqlalchemy import (
    String,
    ForeignKey,
    Computed,
    Index,
    UniqueConstraint,
    CheckConstraint, SQLColumnExpression, select, func, case,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import mapped_column, Mapped, relationship, MappedAsDataclass, query_expression

from database.postgres.base import Base
from database.postgres.model_types import bigint_pk
from database.postgres.pgivm import BaseImmvORMMixin

__all__ = (
    'UpdatedAtMixin',
    'AssetOperationType',
    'UserAssetAddress',
    'AssetTicker',
    'UserAssetOperation',
    'UserAsset',
    'AssetTickerPrice',
    'AssetPopularity',
)


class UpdatedAtMixin(MappedAsDataclass):
    updated_at: Mapped[datetime.datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class AssetOperationType(enum.StrEnum):
    PURCHASE = 'PURCHASE'
    SELL = 'SELL'


class UserAssetAddress(Base):
    __tablename__ = 'user_asset_addresses'

    id: Mapped[bigint_pk] = mapped_column(init=False)
    public_key: Mapped[str]
    user_id: Mapped[uuid.UUID]
    wallet_name: Mapped[list[str] | None] = mapped_column(
        MutableList.as_mutable(ARRAY(String(50))),
        default=None,
    )

    linked_operations: Mapped[list[UserAssetOperation]] = relationship(
        'UserAssetOperation',
        back_populates='address',
        passive_deletes=True,
        default_factory=list,
        lazy='write_only',
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'public_key',  name='user_key_uq'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.wallet_name = })'


class AssetTicker(Base):
    __tablename__ = 'asset_tickers'

    name: Mapped[Annotated[str, mapped_column(String(50), primary_key=True)]]

    __table_args__ = (
        CheckConstraint('name = upper(name)', name='name_is_upper'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.name = })'


class AssetTickerPrice(Base):
    __tablename__ = 'asset_tickers_price'

    id: Mapped[bigint_pk] = mapped_column(init=False)
    name: Mapped[str] = mapped_column(
        ForeignKey('asset_tickers.name', ondelete='CASCADE'),
    )
    price: Mapped[decimal.Decimal]
    updated_at: Mapped[datetime.datetime]
    saved_at: Mapped[datetime.datetime] = mapped_column(
        init=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    outdated: Mapped[bool] = query_expression()

    __table_args__ = (
        CheckConstraint('price > 0', name='positive_price_check'),
        Index('ix_updated_at', 'updated_at'),
        UniqueConstraint('name', name='name_uq'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} @ {self.price})'


class UserAssetOperation(Base):
    __tablename__ = 'user_asset_operations'

    id: Mapped[bigint_pk] = mapped_column(init=False)
    time: Mapped[datetime.datetime]
    type: Mapped[enum.Enum] = mapped_column(
        ENUM(AssetOperationType, name='asset_operation_type'),
    )
    user_asset_id: Mapped[int] = mapped_column(
        ForeignKey('user_assets.id', ondelete='CASCADE'),
    )
    quantity: Mapped[decimal.Decimal]
    unit_price: Mapped[decimal.Decimal]
    summ: Mapped[decimal.Decimal] = mapped_column(
        Computed('unit_price * quantity'),
        init=False,
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey('user_asset_addresses.id', ondelete='RESTRICT')
    )

    asset: Mapped[UserAsset] = relationship(
        'UserAsset',
        back_populates='operations',
        init=False,
        passive_deletes=True,
    )
    address: Mapped[UserAssetAddress] = relationship(
        'UserAssetAddress',
        back_populates='linked_operations',
        init=False,
        passive_deletes=True,
    )

    __table_args__ = (
        Index('ix_user_asset_id', 'user_asset_id'),
        CheckConstraint('quantity > 0', name='asset_qty_gt_0'),
        CheckConstraint('unit_price > 0', name='unit_price_gt_0'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.user_asset_id = })'


class UserAsset(Base):
    __tablename__ = 'user_assets'

    id: Mapped[bigint_pk] = mapped_column(init=False)
    name: Mapped[str]
    ticker_id: Mapped[Annotated[str, mapped_column(
        ForeignKey('asset_tickers.name', ondelete='RESTRICT'))]
    ]
    user_id: Mapped[uuid.UUID]  # from KeyCloak

    __table_args__ = (
        UniqueConstraint('user_id', 'ticker_id', name='user_asset_uq'),
    )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.name})'

    operations: Mapped[list[UserAssetOperation]] = relationship(
        UserAssetOperation,
        back_populates='asset',
        passive_deletes=True,
        init=False,
        default_factory=list,
    )
    ticker: Mapped[AssetTicker] = relationship(
        AssetTicker,
        passive_deletes=True,
        init=False
    )

    @hybrid_property
    def balance(self) -> decimal.Decimal:
        return sum(
            (op.summ if op.type == AssetOperationType.PURCHASE else - op.summ for op in self.operations),
            start=decimal.Decimal(0)
        )

    # noinspection PyNestedDecorators
    @balance.inplace.expression
    @classmethod
    def _balance_expression(cls) -> SQLColumnExpression[decimal.Decimal]:
        return select(
            func.coalesce(
            func.sum(
                case(
                (UserAssetOperation.type == 'PURCHASE', UserAssetOperation.summ),
                    else_= - UserAssetOperation.summ,
                    )
                ),
                decimal.Decimal(0),
            ),
        ).where(
            UserAssetOperation.user_asset_id == cls.id,
        ).label(
            'balance_in_usdt',
        )


class AssetPopularity(BaseImmvORMMixin, Base):
    """IMMV model for asset popularity (number of users per ticker).
    replica_identity_full is needed for logical replication support.
    """
    __tablename__ = "asset_popularity"
    is_view = True
    replica_identity_full = True

    ticker_id: Mapped[str] = mapped_column(primary_key=True)
    num_usages: Mapped[int] = mapped_column()

    selectable = select(
        UserAsset.ticker_id,
        func.count().label("num_usages"),
    ).select_from(
        UserAsset,
    ).group_by(
        UserAsset.ticker_id,
    )
