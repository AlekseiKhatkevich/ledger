from functools import cache

from sqlalchemy import cast, exists, literal, select, insert

from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetOperation
from logic.repositories.user_asset_operation import BaseUserAssetOperationRepository


@cache
class PostgresUserAssetOperationRepository(PostgresBaseRepository, BaseUserAssetOperationRepository):
    model = UserAssetOperation

    async def check_asset_and_address_exists(self, data: UserAssetOperationData) -> tuple[bool, bool]:
        UserAsset = UserAssetOperation.asset.property.mapper.class_
        UserAssetAddress = UserAssetOperation.address.property.mapper.class_

        asset_exists_stmt = exists().where(
            UserAsset.user_id == data.user_id,
            UserAsset.id == data.user_asset_id,
        )
        address_exists_stmt = exists().where(
            UserAssetAddress.user_id == data.user_id,
            UserAssetAddress.id == data.address_id,
        )
        async with self.db.session() as session:
            resp = await session.execute(select(asset_exists_stmt, address_exists_stmt))
            return resp.one()

    async def insert_if_valid(
        self,
        data: UserAssetOperationData,
    ) -> tuple[UserAssetOperation | None, bool, bool]:
        """Одним SQL-запросом проверяет существование asset и address,
        и если оба существуют — вставляет запись.

        Возвращает:
            (модель | None, asset_exists, address_exists)
        """
        UserAsset = UserAssetOperation.asset.property.mapper.class_
        UserAssetAddress = UserAssetOperation.address.property.mapper.class_

        # CTE: проверка существования asset
        asset_check = (
            select(
                exists()
                .where(UserAsset.user_id == data.user_id, UserAsset.id == data.user_asset_id)
                .label("ok")
            )
            .cte("asset_check")
        )

        # CTE: проверка существования address
        address_check = (
            select(
                exists()
                .where(UserAssetAddress.user_id == data.user_id, UserAssetAddress.id == data.address_id)
                .label("ok")
            )
            .cte("address_check")
        )

        # CTE с данными для вставки (literal + cast, чтобы типы совпадали с колонками)
        data_cte = (
            select(
                literal(data.time).label("time"),
                cast(literal(data.type), UserAssetOperation.type.type).label("type"),
                literal(data.user_asset_id).label("user_asset_id"),
                literal(data.quantity).label("quantity"),
                literal(data.unit_price).label("unit_price"),
                literal(data.address_id).label("address_id"),
            )
            .cte("data_cte")
        )

        # CTE: INSERT с WHERE — строка вставится только если обе проверки прошли
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
                select(data_cte).where(
                    select(asset_check.c.ok).scalar_subquery(),
                    select(address_check.c.ok).scalar_subquery(),
                ),
            )
            .returning(UserAssetOperation.id)
            .cte("insert_op")
        )

        # Финальный SELECT: флаги проверок + id вставленной записи (NULL если не вставилось)
        final_stmt = select(
            select(asset_check.c.ok).scalar_subquery().label("asset_exists"),
            select(address_check.c.ok).scalar_subquery().label("address_exists"),
            select(insert_op.c.id).scalar_subquery().label("inserted_id"),
        )

        async with self.db.session() as session:
            row = await session.execute(final_stmt)
            await session.commit()
            asset_exists, address_exists, inserted_id = row.one()

            if inserted_id is None:
                return None, asset_exists, address_exists

            model = await self.get_by_id(inserted_id)
            return model, asset_exists, address_exists
