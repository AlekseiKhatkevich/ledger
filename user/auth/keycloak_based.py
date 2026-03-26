import uuid
from functools import cache, cached_property

from keycloak import KeycloakOpenID, KeycloakAdmin

from config import settings
from user.domain import UserCreateIn


@cache
class KeyCloakAuth:
    # https: // anqorithm.medium.com / integrating - fastapi -
    # with-keycloak -for -authentication-151d0996afbc
    """KeyKloak auth for user tokens and stuff"""
    def __init__(
            self,
            server_url: str | None = None,
            client_id: str | None = None,
            realm_name: str | None = None,
            client_secret_key: str | None = None,
            pool_maxsize: str | None = None,
            admin_username: str | None = None,
            admin_password: str | None = None,
            admin_user_realm_name: str = 'master'
    ) -> None:
        self.server_url = server_url or settings.KEYCLOAK_SERVER_URL
        self.client_id = client_id or settings.KEYCLOAK_CLIENT_ID
        self.realm_name = realm_name or settings.KEYCLOAK_REALM
        self.client_secret_key = client_secret_key or settings.KEYCLOAK_CLIENT_SECRET
        self.pool_maxsize = pool_maxsize or settings.KEYCLOAK_POOL_MAXSIZE
        self.admin_username = admin_username or settings.KEYCLOAK_ADMIN
        self.admin_password = admin_password or settings.KEYCLOAK_ADMIN_PASSWORD
        self.admin_user_realm_name = admin_user_realm_name


    @cached_property
    def keycloak_admin(self) -> KeycloakAdmin:
        return KeycloakAdmin(
            server_url=self.server_url,
            username=self.admin_username,
            password=self.admin_password,
            realm_name=self.realm_name,
            user_realm_name=self.admin_user_realm_name,
            pool_maxsize=self.pool_maxsize,
        )

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
        """Get tokens by login // password"""
        return await self.keycloak_openid.a_token(user, password)

    async def verify_token(self, token: str) -> dict:
        """Verifies token and returns user information"""
        return await self.keycloak_openid.a_userinfo(token)

    async def refresh_token(self, refresh_token: str) -> dict:
        """Refreshes token"""
        return await self.keycloak_openid.a_refresh_token(refresh_token)

    async def create_user(self, user_data: UserCreateIn) -> uuid.UUID:
        """Creates user in KeyCloak"""
        new_user = await self.keycloak_admin.a_create_user(
            dict(
                email=user_data.email,
                username=user_data.username,
                enabled=True,
                firstName=user_data.first_name,
                lastName=user_data.last_name,
                exist_ok=user_data.exist_ok,
                credentials=[{'value': user_data.password, 'type': user_data.type,}],
                attributes={'locale': [user_data.locale,]}
            )
        )
        return uuid.UUID(new_user)
