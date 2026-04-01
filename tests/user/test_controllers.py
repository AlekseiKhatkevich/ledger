import msgspec
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from user.controllers import UserController
from user.domain import CreatedUserOut


def test_userinfo(test_client, kc_userinfo_response, kc_userinfo_api_mock):
    response = test_client.get(
        UserController.path,
    )
    assert response.status_code == HTTP_200_OK
    assert response.json() == kc_userinfo_response


def test_create_user(
        test_client_no_auth,
        user_create_in,
        kc_create_new_user_api_mock,
        kc_get_user_api_mock,
        kc_auth,
):
    response = test_client_no_auth.post(
        UserController.path + '/create',
        json=msgspec.to_builtins(user_create_in),
    )

    assert response.status_code == HTTP_201_CREATED
    assert CreatedUserOut(**response.json())