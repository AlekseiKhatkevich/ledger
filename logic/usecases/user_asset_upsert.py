from api.user_assets.domain import UserAssetData
from database.postgres.repositories.user_asset import PostgresUserAssetRepository


class UserAssetUpsertUseCase:
    @staticmethod
    async def execute(data: UserAssetData) ->  int | None:
        return await PostgresUserAssetRepository().upsert(data)
