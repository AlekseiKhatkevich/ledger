import uuid
from functools import cache
from typing import Any

from sqlalchemy import (
    CTE,
    ColumnElement,
    Select,
    cast,
    exists,
    insert,
    literal,
    select,
    update,
)

from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetOperation
from logic.repositories.user_asset_operation import BaseUserAssetOperationRepository


@cache
class PostgresUserAssetOperationRepository(PostgresBaseRepository, BaseUserAssetOperationRepository):
    model = UserAssetOperation

    @staticmethod
    def _build_asset_check_cte(
        user_id: uuid.UUID,
        user_asset_id: int,
    ) -> CTE:
        UserAsset = UserAssetOperation.asset.property.mapper.class_
        return (
            select(
                exists()
                .where(UserAsset.user_id == user_id, UserAsset.id == user_asset_id)
                .label("ok"),
            )
            .cte("asset_check")
        )

    @staticmethod
    def _build_address_check_cte(
        user_id: uuid.UUID,
        address_id: int,
    ) -> CTE:
        UserAssetAddress = UserAssetOperation.address.property.mapper.class_
        return (
            select(
                exists()
                .where(UserAssetAddress.user_id == user_id, UserAssetAddress.id == address_id)
                .label("ok"),
            )
            .cte("address_check")
        )

    @staticmethod
    def _build_value_columns(
        data: UserAssetOperationData,
    ) -> list[ColumnElement[Any]]:
        return [
            literal(data.time).label("time"),
            cast(literal(data.type), UserAssetOperation.type.type).label("type"),
            literal(data.user_asset_id).label("user_asset_id"),
            literal(data.quantity).label("quantity"),
            literal(data.unit_price).label("unit_price"),
            literal(data.address_id).label("address_id"),
        ]

    @staticmethod
    def _build_final_select(
        asset_check: CTE,
        address_check: CTE,
        op_cte: CTE,
    ) -> Select:
        return select(
            select(asset_check.c.ok).scalar_subquery().label("asset_exists"),
            select(address_check.c.ok).scalar_subquery().label("address_exists"),
            select(op_cte.c.id).scalar_subquery().label("op_id"),
        )

    async def insert_if_valid(
        self,
        data: UserAssetOperationData,
    ) -> tuple[int | None, bool, bool]:
        asset_check = self._build_asset_check_cte(data.user_id, data.user_asset_id)
        address_check = self._build_address_check_cte(data.user_id, data.address_id)

        values = self._build_value_columns(data)

        insert_op = (
            insert(UserAssetOperation)
            .from_select(
                [
                    UserAssetOperation.time,
                    UserAssetOperation.type,
                    UserAssetOperation.user_asset_id,
                    UserAssetOperation.quantity,
                    UserAssetOperation.unit_price,
                    UserAssetOperation.address_id,
                ],
                select(*values).where(
                    select(asset_check.c.ok).scalar_subquery(),
                    select(address_check.c.ok).scalar_subquery(),
                ),
            )
            .returning(UserAssetOperation.id)
            .cte("insert_op")
        )

        final_stmt = self._build_final_select(asset_check, address_check, insert_op)

        async with self.db.session() as session:
            row = await session.execute(final_stmt)
            await session.commit()
            asset_exists, address_exists, inserted_id = row.one()

            return inserted_id, asset_exists, address_exists

    async def update_if_valid(
        self,
        data: UserAssetOperationData,
    ) -> tuple[int | None, bool, bool]:
        asset_check = self._build_asset_check_cte(data.user_id, data.user_asset_id)
        address_check = self._build_address_check_cte(data.user_id, data.address_id)

        values = self._build_value_columns(data)

        sq = (
            select(*values)
            .where(
                select(asset_check.c.ok).scalar_subquery(),
                select(address_check.c.ok).scalar_subquery(),
            )
            .subquery("sq")
        )

        update_op = (
            update(UserAssetOperation)
            .values(
                {
                    UserAssetOperation.time: sq.c.time,
                    UserAssetOperation.type: sq.c.type,
                    UserAssetOperation.user_asset_id: sq.c.user_asset_id,
                    UserAssetOperation.quantity: sq.c.quantity,
                    UserAssetOperation.unit_price: sq.c.unit_price,
                    UserAssetOperation.address_id: sq.c.address_id,
                },
            )
            .where(UserAssetOperation.id == data.id)
            .returning(UserAssetOperation.id)
            .cte("update_op")
        )

        final_stmt = self._build_final_select(asset_check, address_check, update_op)

        async with self.db.session() as session:
            row = await session.execute(final_stmt)
            await session.commit()
            asset_exists, address_exists, updated_id = row.one()

            return updated_id, asset_exists, address_exists
