import abc
from typing import Any

from user.auth.keycloak_based import KeyCloakAuth


class KeyCloakBaseUseCase(abc.ABC):
    def __init__(self, auth_provider: Any | None = None) -> None:
        self.auth_provider = auth_provider or KeyCloakAuth()

    @abc.abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        pass
