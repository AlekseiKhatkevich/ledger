from aux.helpers.serialization import convert_dash_to_underscore
from user.auth.keycloak_based import KeyCloakAuth


class KeyCloakRefreshUseCase:
    """To refresh KeyCloak token"""
    @staticmethod
    async def execute(refresh_token: str) -> dict:
        return_data = await KeyCloakAuth().refresh_token(refresh_token)
        return convert_dash_to_underscore(return_data, keys=('not-before-policy',))
