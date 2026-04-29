import msgspec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from user.controllers import UserController
from user.domain import CreatedUserOut


async def test_userinfo(test_client, kc_userinfo_response):
    response = await test_client.get(
        UserController.path + '/via-backend',
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == kc_userinfo_response


async def test_create_user(
        test_client_no_auth,
        user_create_in,
        kc_create_new_user_api_mock,
        kc_get_user_api_mock,
        kc_auth,
):
    response = await test_client_no_auth.post(
        UserController.path + '/create',
        json=msgspec.to_builtins(user_create_in),
    )

    assert response.status_code == HTTP_201_CREATED
    assert CreatedUserOut(**response.json())