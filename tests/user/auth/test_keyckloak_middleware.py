from unittest.mock import Mock

import pytest
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware import AuthenticationResult

from config import settings
from main import app
from user.auth.keycloack_middleware import KeyCloakAuthenticationMiddleware
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import KeyCloakToken, User


@pytest.fixture
def kc_auth_middleware(kc_auth: KeyCloakAuth) -> KeyCloakAuthenticationMiddleware:
    return KeyCloakAuthenticationMiddleware(auth_provider=kc_auth, app=app)

@pytest.fixture
def connection() -> Mock:
    connection = Mock(spec_set=ASGIConnection)
    connection.headers = {settings.KEYCLOAK_API_KEY_HEADER: 'Bearer i_am_a_fake_jwt_token'}
    return connection


async def test_kc_auth_middleware_negative_no_header(kc_auth_middleware, connection):
    connection.headers = {}

    with pytest.raises(NotAuthorizedException, match='No token provided'):
        await kc_auth_middleware.authenticate_request(connection)


@pytest.mark.parametrize('kc_userinfo_api_mock', (401, ), indirect=True)
async def test_kc_auth_middleware_negative_invalid_token(
        kc_auth_middleware,
        kc_userinfo_api_mock,
        connection,
):
    with pytest.raises(NotAuthorizedException, match='Wrong or outdated token'):
        await kc_auth_middleware.authenticate_request(connection)


async def test_kc_auth_middleware_positive(
        kc_auth_middleware,
        kc_userinfo_api_mock,
        kc_userinfo_response,
        connection,
):
    auth_result = await kc_auth_middleware.authenticate_request(connection)

    assert isinstance(auth_result, AuthenticationResult)
    assert isinstance(auth_result.user, User)
    assert isinstance(auth_result.auth, KeyCloakToken)
    assert auth_result.user == User(**kc_userinfo_response)
    assert auth_result.auth.api_key == 'i_am_a_fake_jwt_token'
