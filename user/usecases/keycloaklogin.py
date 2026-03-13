from aux.helpers.serialization import convert_dash_to_underscore
from user.auth.keycloak_based import KeyCloakAuth

class KeyCloakLoginUseCase:

    @staticmethod
    async def execute(user_id: str, password: str) -> dict:
        return_data = await KeyCloakAuth().get_token(user_id, password, )
        return convert_dash_to_underscore(return_data, keys=('not-before-policy',))