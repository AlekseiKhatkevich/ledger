import msgspec
import pytest

from user.usecases.keycloak_create_user import KeyCloakCreateUserUseCase


@pytest.fixture
def usecase(kc_auth):
    return KeyCloakCreateUserUseCase(auth_provider=kc_auth)

async def test_kc_create_user_usecase_positive(
    kc_create_new_user_api_mock,
    user_create_in,
    kc_get_user_api_mock,
    user_from_get_user,
    usecase,
    ):
    response = await usecase.execute(user_create_in)
    assert response == msgspec.to_builtins(user_from_get_user)

