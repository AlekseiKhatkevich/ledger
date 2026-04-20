from functools import cache

from database.postgres.repositories.base_repository import PostgresBaseRepository
from logic.db_models import UserAsset
from logic.repositories.user_asset import BaseUserAssetRepository


@cache
class PostgresUserAssetRepository(PostgresBaseRepository, BaseUserAssetRepository):
    model = UserAsset
