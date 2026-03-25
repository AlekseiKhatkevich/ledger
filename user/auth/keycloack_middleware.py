from keycloak import KeycloakAuthenticationError
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AbstractAuthenticationMiddleware, AuthenticationResult

from config import settings
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import KeyCloakToken, User


class KeyCloakAuthenticationMiddleware(AbstractAuthenticationMiddleware):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._keycloak_auth_provider = KeyCloakAuth()

    async def authenticate_request(self, connection: ASGIConnection) -> AuthenticationResult:
        """
        Given a request, parse the request api key stored in the header and
        retrieve the user correlating to the token from the DB"""

        auth_header = connection.headers.get(settings.KEYCLOAK_API_KEY_HEADER)
        if not auth_header:
            raise NotAuthorizedException(detail='No token provided',)
        try:
            user = User(** await self._keycloak_auth_provider.verify_token(auth_header))
        except KeycloakAuthenticationError:
            raise NotAuthorizedException(
                detail='Wrong or outdated token',
                extra={'token': auth_header},
            ) from None
        return AuthenticationResult(user=user, auth=KeyCloakToken(api_key=auth_header))

#  todo эндпоинт создания юзера в кейклок
# todo tests
