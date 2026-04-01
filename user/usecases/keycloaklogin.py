from typing import Any

from aux.helpers.serialization import convert_dash_to_underscore
from user.auth.keycloak_based import KeyCloakAuth

class KeyCloakLoginUseCase:
    """For obtaining a bunch of OpenID tokens from Keycloak with login // password"""
    def __init__(self, auth_provider: Any | None = None) -> None:
        self.auth_provider = auth_provider or KeyCloakAuth()

    async def execute(self, user_id: str, password: str) -> dict:
        return_data = await self.auth_provider.get_token(user_id, password, )
        return convert_dash_to_underscore(return_data, keys=('not-before-policy',))
