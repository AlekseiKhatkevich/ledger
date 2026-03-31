import uuid

import msgspec


async def test_get_token(kc_get_token_api_mock, kc_get_token_response, kc_auth):
    token_data = await kc_auth.get_token('test@disroot.org', '1q2w3e')
    assert token_data == kc_get_token_response


async def test_verify_token(kc_userinfo_api_mock, kc_userinfo_response, kc_auth):
    userinfo = await kc_auth.verify_token(token='random_token_here')
    assert userinfo == kc_userinfo_response


async def test_refresh_token(kc_refresh_token_api_mock, kc_get_token_response, kc_auth):
    token = await kc_auth.refresh_token(kc_get_token_response['refresh_token'])
    assert token == kc_get_token_response

async def test_create_user(
        user_create_in,
        kc_create_new_user_api_mock,
        kc_auth,
):
    created_user_uuid = kc_create_new_user_api_mock
    response = await kc_auth.create_user(user_create_in)
    assert response == created_user_uuid

async def test_get_user(kc_auth, kc_get_user_api_mock, user_from_get_user):
    user_uuid = kc_get_user_api_mock
    response = await kc_auth.get_user(user_uuid)
    assert response == msgspec.to_builtins(user_from_get_user)
