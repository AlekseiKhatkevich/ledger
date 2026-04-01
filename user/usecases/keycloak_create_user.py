from keycloak import KeycloakPostError

from user.auth.exceptions import DuplicateUserException
from user.domain import UserCreateIn
from user.usecases.keycloak_base import KeyCloakBaseUseCase


class KeyCloakCreateUserUseCase(KeyCloakBaseUseCase):
    """Create new user in KeyCloak"""
    async def execute(self, user_data: UserCreateIn) -> dict:
        try:
            new_user_id = await self.auth_provider.create_user(user_data)
        except KeycloakPostError:
            raise DuplicateUserException(message='User exists with same email')

        return await self.auth_provider.get_user(new_user_id)

