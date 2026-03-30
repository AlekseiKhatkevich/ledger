from user.auth.keycloak_based import KeyCloakAuth

auth = KeyCloakAuth()


async def test_get_token(kc_get_token_api_mock, kc_get_token_response):
    token_data = await auth.get_token('test@disroot.org', '1q2w3e')
    assert token_data == kc_get_token_response


async def test_verify_token(kc_userinfo_api_mock, kc_userinfo_response):
    userinfo = await auth.verify_token(token='random_token_here')
    assert userinfo == kc_userinfo_response


async def test_refresh_token(kc_refresh_token_api_mock, kc_get_token_response):
    token = await auth.refresh_token(kc_get_token_response['refresh_token'])
    assert token == kc_get_token_response

