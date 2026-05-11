from api.user_asset_operations.domain import UserAssetOperationData
from database.postgres.repositories.base_repository import PostgresBaseRepository
from database.postgres.connection import db as _db
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_address import PostgresUserAssetAddressRepository
from logic.db_models import UserAsset, UserAssetAddress
from logic.exceptions import UserAssetNotFoundError, UserAssetAddressNotFoundError


class UserAssetOperationUseCase:

    def __iter__(self) -> None:
        self.user_asset_repository = PostgresUserAssetRepository()
        self.user_asset_address_repository = PostgresUserAssetAddressRepository()

    async def execute(self, data: UserAssetOperationData) -> UserAssetOperationData:
        # Один SQL-запрос: проверяем существование обоих объектов
        asset_exists, address_exists = await PostgresBaseRepository.check_both_exist(
            db=_db,
            model_a=UserAsset,
            filters_a={'id': data.user_asset_id, 'user_id': data.user_id},
            model_b=UserAssetAddress,
            filters_b={'id': data.address_id, 'user_id': data.user_id},
        )

        if not asset_exists:
            raise UserAssetNotFoundError(extra={'id': data.user_asset_id})

        if not address_exists:
            raise UserAssetAddressNotFoundError(extra={'id': data.address_id})

