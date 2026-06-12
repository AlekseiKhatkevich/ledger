import abc
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from logic.db_models import UserAssetOperation
    from api.user_asset_operations.domain import UserAssetOperationSearchByNoteInputArgs


class BaseUserAssetOperationRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, id: int) -> UserAssetOperation:
        pass

    @abc.abstractmethod
    async def get_by_notes(
        self,
        search_args: UserAssetOperationSearchByNoteInputArgs
    ) -> list[tuple['UserAssetOperation', list[dict]]]:
        """Get operations filtered by note text."""
        pass
