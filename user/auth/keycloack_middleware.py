from typing import Any

import msgspec
from jwcrypto.jwt import JWT
from keycloak import KeycloakAuthenticationError
from litestar.connection import ASGIConnection
from litestar.datastructures import Headers
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

from config import settings
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import KeyCloakToken, User


class KeyCloakAuthenticationMiddlewareBase(AbstractAuthenticationMiddleware):

    @staticmethod
    def get_token(headers: Headers) -> str:
        auth_header = headers.get(settings.KEYCLOAK_API_KEY_HEADER)
        if not auth_header:
            raise NotAuthorizedException(detail='No token provided')
        _, token_str = auth_header.split(f'{settings.KEYCLOAK_API_KEY_HEADER_PREFIX} ', 1)
        return token_str


class JWTAuthenticationMiddleware(KeyCloakAuthenticationMiddlewareBase):
    """
    This MW just gets a user info from Caddy. Caddy should validate token with KC by itself beforehand.
    """
    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        auth_header = self.get_token(connection.headers)
        try:
            jwt = JWT(jwt=auth_header)
        except ValueError:
            raise NotAuthorizedException(
                detail='Wrong or damaged token',
                extra={'token': auth_header},
            ) from None
        payload = jwt.token.objects['payload']
        user = msgspec.json.decode(payload, type=User)
        return AuthenticationResult(user=user, auth=KeyCloakToken(api_key=auth_header))


class KeyCloakAuthenticationMiddleware(KeyCloakAuthenticationMiddlewareBase):

    def __init__(self, auth_provider: Any | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keycloak_auth_provider = auth_provider or KeyCloakAuth()

    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """
        Given a request, parse the request api key stored in the header and
        retrieve the user correlating to the token from the DB"""
        auth_header = self.get_token(connection.headers)
        try:
            user = User(**await self._keycloak_auth_provider.verify_token(auth_header))
        except KeycloakAuthenticationError:
            raise NotAuthorizedException(
                detail='Wrong or outdated token',
                extra={'token': auth_header},
            ) from None
        return AuthenticationResult(user=user, auth=KeyCloakToken(api_key=auth_header))
