import abc
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from logic.db_models import UserAsset


class BaseUserAssetRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, _id: str) -> UserAsset:
        pass