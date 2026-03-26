from keycloak import KeycloakPostError

from user.auth.exceptions import DuplicateUserException
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import UserCreateIn


class KeyCloakCreateUserUseCase:
    """Create new user in KeyCloak"""

    @staticmethod
    async def execute(user_data: UserCreateIn) -> dict:
        kc = KeyCloakAuth()
        try:
            new_user_id = await kc.create_user(user_data)
        except KeycloakPostError as err:
            raise DuplicateUserException(message='User exists with same email')

        return await kc.get_user(new_user_id)
