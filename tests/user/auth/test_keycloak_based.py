from user.auth.keycloak_based import KeyCloakAuth

auth = KeyCloakAuth()

'http://keycloak:8080/realms/test/protocol/openid-connect/token'
# {'data': {'client_id': 'fastapi-keycloak', 'client_secret': 'rhG99IM6reLnkpVRYyT7XjTKt7AVYe8q', 'code': '', 'grant_type': 'password', 'password': '1q2w3e', 'redirect_uri': '', 'scope': 'openid', 'username': 'qwerty12345@disroot.org'}}
# headers --  {'Content-Type': 'application/x-www-form-urlencoded'}


async def test_get_token(kc_get_token_api_mock, kc_get_token_response):
    token_data = await auth.get_token('test@disroot.org', '1q2w3e')
    assert token_data == kc_get_token_response


async def test_verify_token(kc_userinfo_api_mock, kc_userinfo_response):
    userinfo = await auth.verify_token(token='random_token_here')
    assert userinfo == kc_userinfo_response

async def test_refresh_token():
    pass

