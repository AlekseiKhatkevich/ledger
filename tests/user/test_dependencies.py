from litestar.testing import RequestFactory

from user.dependencies import keycloak_user


async def test_keycloak_user(user):
    request = RequestFactory().get('/', user=user)

    returned_user = await keycloak_user(request)

    assert returned_user == user