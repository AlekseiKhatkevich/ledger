from typing import Any

from keycloak import KeycloakPostError

from user.auth.exceptions import DuplicateUserException
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import UserCreateIn


class KeyCloakCreateUserUseCase:
    """Create new user in KeyCloak"""
    def __init__(self, auth_provider: Any | None = None) -> None:
        self.auth_provider = auth_provider or KeyCloakAuth()

    async def execute(self, user_data: UserCreateIn) -> dict:
        try:
            new_user_id = await self.auth_provider.create_user(user_data)
        except KeycloakPostError:
            raise DuplicateUserException(message='User exists with same email')

        return await self.auth_provider.get_user(new_user_id)

