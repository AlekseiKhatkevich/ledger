import abc
from typing import TYPE_CHECKING

from api.user_assets.domain import UserAssetData

if TYPE_CHECKING:
    from logic.db_models import UserAsset


class BaseUserAssetRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, _id: str) -> UserAsset:
        pass

    @abc.abstractmethod
    async def upsert(self, data: UserAssetData) -> None:
        pass