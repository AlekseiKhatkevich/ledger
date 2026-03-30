from user.auth.keycloak_based import KeyCloakAuth

auth = KeyCloakAuth()

'http://keycloak:8080/realms/test/protocol/openid-connect/token'
# {'data': {'client_id': 'fastapi-keycloak', 'client_secret': 'rhG99IM6reLnkpVRYyT7XjTKt7AVYe8q', 'code': '', 'grant_type': 'password', 'password': '1q2w3e', 'redirect_uri': '', 'scope': 'openid', 'username': 'qwerty12345@disroot.org'}}
# headers --  {'Content-Type': 'application/x-www-form-urlencoded'}


async def test_get_token(kc_get_token_api_mock):
    token_data = await auth.get_token('test@disroot.org', '1q2w3e')
    assert token_data['access_token']
    assert token_data['expires_in']
    assert token_data['refresh_expires_in']
    assert token_data['token_type']
    assert token_data['id_token']
    assert token_data['not-before-policy']
    assert token_data['session_state']
    assert token_data['scope']

