import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logic.db_models import UserAssetOperation


class BaseUserAssetOperationRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, id: int) -> UserAssetOperation:
        pass
