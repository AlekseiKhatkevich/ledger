import abc
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from logic.db_models import UserAssetAddress


class BaseUserAssetAddressRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_pubkey(self, pkey: str) -> UserAssetAddress:
        pass