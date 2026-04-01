from aux.helpers.serialization import convert_dash_to_underscore
from user.usecases.keycloaklogin import KeyCloakLoginUseCase


async def test_kc_login_use_case_positive(
    kc_get_token_api_mock,
    kc_auth,
    kc_get_token_response,
):
    usecase = KeyCloakLoginUseCase(auth_provider=kc_auth)

    response = await usecase.execute(user_id='user_id', password='user_password')

    assert response == convert_dash_to_underscore(
        kc_get_token_response,
        keys=('not-before-policy',),
    )
