from aux.helpers.serialization import convert_dash_to_underscore
from user.usecases.keycloak_base import KeyCloakBaseUseCase


class KeyCloakLoginUseCase(KeyCloakBaseUseCase):
    """For obtaining a bunch of OpenID tokens from Keycloak with login // password"""

    async def execute(self, user_id: str, password: str) -> dict:
        return_data = await self.auth_provider.get_token(user_id, password, )
        return convert_dash_to_underscore(return_data, keys=('not-before-policy',))
