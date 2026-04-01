from user.controllers import UserController


def test_userinfo(test_client, kc_userinfo_response, kc_userinfo_api_mock):
    response = test_client.get(
        UserController.path,
    )
    assert response.json() == kc_userinfo_response