import uuid

from api.user_assets.domain import UserAssetData, UserAssetAggregatedPage
from database.postgres.repositories.user_asset import PostgresUserAssetRepository
from database.postgres.repositories.user_asset_operation import PostgresUserAssetOperationRepository


class UserAssetUpsertUseCase:

    @staticmethod
    async def execute(data: UserAssetData) ->  int | None:
        return await PostgresUserAssetRepository().upsert(data)


class UserAssetListUseCase:

    @staticmethod
    async def execute(
            user_id: uuid.UUID,
            last_ticker_id: str | None,
            page_size: int,
    ) -> UserAssetAggregatedPage:
        return await PostgresUserAssetOperationRepository().get_user_asset_aggregates(
            user_id,
            page_size,
            last_ticker_id,
        )