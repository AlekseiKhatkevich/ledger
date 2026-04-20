from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAssetOperation
from logic.repositories.user_asset_operation import BaseUserAssetOperationRepository


@cache
class PostgresUserAssetOperationRepository(PostgresBaseRepository, BaseUserAssetOperationRepository):
    model = UserAssetOperation
