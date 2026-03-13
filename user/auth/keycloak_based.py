from functools import cache, cached_property

from keycloak import KeycloakOpenID

from config import Settings

@cache
class KeyCloakAuth:
    def __init__(
            self,
            server_url: str | None = None,
            client_id: str | None = None,
            realm_name: str | None = None,
            client_secret_key: str | None = None,
            pool_maxsize: str | None = None,
    ) -> None:
        settings = Settings()
        self.server_url = server_url or settings.KEYCLOAK_SERVER_URL.encoded_string()
        self.client_id = client_id or settings.KEYCLOAK_CLIENT_ID
        self.realm_name = realm_name or settings.KEYCLOAK_REALM
        self.client_secret_key = client_secret_key or settings.KEYCLOAK_CLIENT_SECRET
        self.pool_maxsize = pool_maxsize or settings.KEYCLOAK_POOL_MAXSIZE


    @cached_property
    def keycloak_openid(self) -> KeycloakOpenID:
        return KeycloakOpenID(
            server_url=self.server_url,
            client_id=self.client_id,
            realm_name=self.realm_name,
            client_secret_key=self.client_secret_key,
            pool_maxsize=self.pool_maxsize,
        )

    async def get_token(self, user: str, password: str) -> dict:
        return await self.keycloak_openid.a_token(user, password)

