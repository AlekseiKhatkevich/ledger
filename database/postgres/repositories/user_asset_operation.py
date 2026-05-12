import decimal
import uuid
from functools import cache
from typing import Any

from sqlalchemy import (
    CTE,
    ColumnElement,
    Select,
    case,
    cast,
    exists,
    func,
    insert,
    literal,
    select,
    update,
)

from api.user_asset_operations.domain import UserAssetOperationData, DbCRUDOperationReturnData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import AssetOperationType, UserAssetOperation
from logic.repositories.user_asset_operation import BaseUserAssetOperationRepository

"""
insert ->

WITH asset_check AS (
    SELECT EXISTS (
        SELECT 1
        FROM user_assets
        WHERE user_assets.user_id = '7f4296f5-ba32-434e-9c18-2ad2e40b9526'
          AND user_assets.id = 82
    ) AS ok
),
address_check AS (
    SELECT EXISTS (
        SELECT 1
        FROM user_asset_addresses
        WHERE user_asset_addresses.user_id = '7f4296f5-ba32-434e-9c18-2ad2e40b9526'
          AND user_asset_addresses.id = 99
    ) AS ok
),
balance_check AS (
    SELECT COALESCE(
        SUM(
            CASE
                WHEN type = 'PURCHASE' THEN quantity
                WHEN type = 'SELL' THEN -quantity
                ELSE 0
            END
        ),
        0
    ) AS balance
    FROM user_asset_operations
    WHERE address_id = 99
      AND user_asset_id = 82
),
balance_ok AS (
    SELECT (
        CAST('SELL' AS asset_operation_type) != 'SELL'
        OR (
            CAST('SELL' AS asset_operation_type) = 'SELL'
            AND 100 <= (SELECT balance_check.balance FROM balance_check)
        )
    ) AS ok
),
insert_op AS (
    INSERT INTO user_asset_operations (time, type, user_asset_id, quantity, unit_price, address_id)
    SELECT
        '2026-05-11 16:44:27.015309'::timestamptz     AS time,
        CAST('SELL' AS asset_operation_type)        AS type,
        82                                               AS user_asset_id,
        100                                               AS quantity,
        11                                               AS unit_price,
        99                                               AS address_id
    WHERE (SELECT asset_check.ok FROM asset_check)
      AND (SELECT address_check.ok FROM address_check)
      AND (SELECT balance_ok.ok FROM balance_ok)
    RETURNING id
)
SELECT
    (SELECT asset_check.ok FROM asset_check)     AS asset_exists,
    (SELECT address_check.ok FROM address_check) AS address_exists,
    (SELECT balance_ok.ok FROM balance_ok)       AS balance_ok,
    (SELECT insert_op.id FROM insert_op)         AS inserted_id;

"""



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
    def _build_balance_check_cte(
        address_id: int,
        user_asset_id: int,
        exclude_operation_id: int | None = None,
    ) -> CTE:
        stmt = select(
            func.coalesce(
                func.sum(
                    case(
                        (UserAssetOperation.type == AssetOperationType.PURCHASE, UserAssetOperation.quantity),
                        else_=-UserAssetOperation.quantity,
                    ),
                ),
                0,
            ).label("balance"),
        ).where(
            UserAssetOperation.address_id == address_id,
            UserAssetOperation.user_asset_id == user_asset_id,
        )

        if exclude_operation_id is not None:
            stmt = stmt.where(UserAssetOperation.id != exclude_operation_id)

        return stmt.cte("balance_check")

    @staticmethod
    def _build_balance_ok_cte(
        type_: AssetOperationType,
        quantity: decimal.Decimal,
        balance_check: CTE,
    ) -> CTE:
        return select(
            case(
                (
                    type_ != AssetOperationType.SELL,
                    literal(True),
                ),
                else_=(
                    select(balance_check.c.balance).scalar_subquery() >= quantity
                ),
            ).label("ok"),
        ).cte("balance_ok")

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
        balance_ok: CTE,
        op_cte: CTE,
    ) -> Select:
        return select(
            select(asset_check.c.ok).scalar_subquery().label("asset_exists"),
            select(address_check.c.ok).scalar_subquery().label("address_exists"),
            select(balance_ok.c.ok).scalar_subquery().label("balance_ok"),
            select(op_cte.c.id).scalar_subquery().label("op_id"),
        )

    async def insert_if_valid(
        self,
        data: UserAssetOperationData,
    ) -> DbCRUDOperationReturnData:
        # 1. CTE проверок
        asset_check = self._build_asset_check_cte(data.user_id, data.user_asset_id)
        address_check = self._build_address_check_cte(data.user_id, data.address_id)

        balance_check = self._build_balance_check_cte(
            address_id=data.address_id,
            user_asset_id=data.user_asset_id,
            exclude_operation_id=None,
        )
        balance_ok = self._build_balance_ok_cte(
            type_=data.type,
            quantity=data.quantity,
            balance_check=balance_check,
        )

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
                    select(balance_ok.c.ok).scalar_subquery(),
                ),
            )
            .returning(UserAssetOperation.id)
            .cte("insert_op")
        )

        final_stmt = self._build_final_select(asset_check, address_check, balance_ok, insert_op)

        async with self.db.session() as session:
            row = await session.execute(final_stmt)
            await session.commit()
            asset_exists, address_exists, balance_ok, inserted_id = row.one()

        return DbCRUDOperationReturnData(
                inserted_id,
                asset_exists,
                address_exists,
                balance_ok,
            )


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