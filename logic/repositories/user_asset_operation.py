import abc
import uuid
from typing import TYPE_CHECKING

from api.user_asset_operations.domain import UserAssetOperationsFilter

if TYPE_CHECKING:
    from logic.db_models import UserAssetOperation


class BaseUserAssetOperationRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, id: int) -> UserAssetOperation:
        pass

    @abc.abstractmethod
    async def get_by_notes(
        self,
        user_id: uuid.UUID,
        op_filter: UserAssetOperationsFilter,
        notes: str,
        distance: int,
    ) -> list[tuple['UserAssetOperation', list[dict]]]:
        """Get operations filtered by note text."""
        pass
