import datetime
import uuid
from typing import Any

import pytest
from litestar.status_codes import HTTP_201_CREATED
from polyfactory.pytest_plugin import register_fixture
from pytest_httpx import HTTPXMock

from config import settings
from tests.user.auth.factories import UserCreateInFactory
from user.auth.keycloak_based import KeyCloakAuth
from user.domain import UserCreateIn

register_fixture(UserCreateInFactory)


KEYCLOAK_BASE_API_URL = f'{settings.KEYCLOAK_SERVER_URL}realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/'


@pytest.fixture
def kc_auth() -> KeyCloakAuth:
    auth = KeyCloakAuth()
    #  avoid extra api call to /refresh
    auth.keycloak_admin.connection._expires_at = (
            datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
    )
    return auth


@pytest.fixture(scope='session')
def kc_get_token_response() -> dict[str, Any]:
    return {
        'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkbHB5NkliMGZOR21WMEx'
                        'TRURDSWs0SUFsZXdsaUc5enI1VGhWY0I5emFvIn0.eyJleHAiOjE3NzQ4NzMwMDgsImlhdC'
                        'I6MTc3NDg3MTIwOCwianRpIjoib25ydHJvOjZhYjk5MGY1LWJkNTMtMTFhOC0wYWI2LTg0N'
                        'jA3MDRjMGZkYSIsImlzcyI6Imh0dHA6Ly9rZXljbG9hazo4MDgwL3JlYWxtcy90ZXN0Iiwi'
                        'YXVkIjoiYWNjb3VudCIsInN1YiI6IjdmNDI5NmY1LWJhMzItNDM0ZS05YzE4LTJhZDJlNDB'
                        'iOTUyNiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImZhc3RhcGkta2V5Y2xvYWsiLCJzaWQiOi'
                        'IyaXNMRjBDbEhNckREdW5hNTRvbGVleWUiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zI'
                        'jpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtdGVzdCIs'
                        'Im9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2V'
                        'zcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY2'
                        '91bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwc'
                        'm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJBbGVrc2VpIEtoYXRrZXZp'
                        'Y2giLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJoYXJkY2FzZSIsImdpdmVuX25hbWUiOiJBbGV'
                        'rc2VpIiwiZmFtaWx5X25hbWUiOiJLaGF0a2V2aWNoIiwiZW1haWwiOiJxd2VydHkxMjM0NU'
                        'BkaXNyb290Lm9yZyJ9.O0Hx6O3IFyk6PW6xZHszGvSLXDlV9iICvP8IveMpJII8BXROZBhy'
                        'HpE_P-fpLkuZDg17iFlbaEHYIQc-L-UtgKUWtbTOW6Ve6kkPnk6dQuawTZ2z8njpdjSV2pa'
                        'MrlW7VoWqQjmGUG6nOi9eyuO8kfXXq9Bysq-i_Es-cMBUBtg1kgm33KcFPFo2PQ80Y-599R'
                        'IQAsPYkrNa0HlEwwzRTzTTOwKWBemcltXFkYXIZrcAiOjfon52XH113x1qG_AMlXYzGaT_f'
                        'z4ukwnSe3_hRd_Fdhmd_6j02dVbzgplzjqeGOgbz_xpYPZpV4YhhxrMiA2Z9MzrUzQO6j8'
                        'AGqQ7ag',
 'expires_in': 1799,
 'refresh_expires_in': 3599,
 'refresh_token': 'eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmMWRlZGQyZS0zZjgxLTQyY2ItYm'
                  'MwOS0yZjRkNzQyYmMwNGMifQ.eyJleHAiOjE3NzQ4NzQ4MDgsImlhdCI6MTc3NDg3MTIwOCwianRpI'
                  'joiM2RlZWI1OTEtMmQ5OC1hOWVjLWQ0ZGMtNmFmN2Y4N2RhMzNlIiwiaXNzIjoiaHR0cDovL2tleWN'
                  'sb2FrOjgwODAvcmVhbG1zL3Rlc3QiLCJhdWQiOiJodHRwOi8va2V5Y2xvYWs6ODA4MC9yZWFsbXMvd'
                  'GVzdCIsInN1YiI6IjdmNDI5NmY1LWJhMzItNDM0ZS05YzE4LTJhZDJlNDBiOTUyNiIsInR5cCI6IlJ'
                  'lZnJlc2giLCJhenAiOiJmYXN0YXBpLWtleWNsb2FrIiwic2lkIjoiMmlzTEYwQ2xITXJERHVuYTU0b'
                  '2xlZXllIiwic2NvcGUiOiJvcGVuaWQgZW1haWwgcm9sZXMgYmFzaWMgd2ViLW9yaWdpbnMgYWNyIHB'
                  'yb2ZpbGUifQ.h6Q_3ayljal-9iSI4uGAD9OmVEmkNZhtNWyP1nfNpCqDeRviT3ND76vTsDf2GPBlNw'
                  'brjiE68BRZpmEssiKZ9g',
 'token_type': 'Bearer',
 'id_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkbHB5NkliMGZOR21WMExTRURDSWs0SUF'
             'sZXdsaUc5enI1VGhWY0I5emFvIn0.eyJleHAiOjE3NzQ4NzMwMDgsImlhdCI6MTc3NDg3MTIwOCwianRpIj'
             'oiNmZmODg0ZDEtOGZiMi1mYzQ5LTBkNmYtOTcwYTZjMGE4NWZjIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrO'
             'jgwODAvcmVhbG1zL3Rlc3QiLCJhdWQiOiJmYXN0YXBpLWtleWNsb2FrIiwic3ViIjoiN2Y0Mjk2ZjUtYmEz'
             'Mi00MzRlLTljMTgtMmFkMmU0MGI5NTI2IiwidHlwIjoiSUQiLCJhenAiOiJmYXN0YXBpLWtleWNsb2FrIiw'
             'ic2lkIjoiMmlzTEYwQ2xITXJERHVuYTU0b2xlZXllIiwiYXRfaGFzaCI6Ii1jcTZfLTdLSnBDdm8tSlRTYl'
             'Z1TEEiLCJhY3IiOiIxIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJBbGVrc2VpIEtoYXRrZXZpY'
             '2giLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJoYXJkY2FzZSIsImdpdmVuX25hbWUiOiJBbGVrc2VpIiwiZmFt'
             'aWx5X25hbWUiOiJLaGF0a2V2aWNoIiwiZW1haWwiOiJxd2VydHkxMjM0NUBkaXNyb290Lm9yZyJ9.Tw-QIj'
             'z8ejh6K6lmI7AIBGcLhAYwXXY2_lRwBt11AY-bA6jS-lsdrPXyEZoj8AR0EetsOs2xd994bFMgxQ5r44FVl'
             'wsOHnwCFkyoV8N3_IR3rrAGwkbn5ECIKnfw6GPb6e1QrQ18jMuaAzLEIKcDKiOQYlB1Z3MkvlFdf70udGbJ'
             'yjKYvvddSTybBmK8tym122IjcWQi14zrT1HOzSvXPqE0qF1PW6LXlMAvp90K6AFVTXvlK5kkWgjmCXxF3jz'
             'mDIPbPleHWxmn8PAhwxmkyL8eUDyNtZnJdRCQ2SkYS1lb8xmC3DQSxYTXTMQuNsDYNRe8LdcxaP9ms7YduQ'
             '2-og',
 'not-before-policy': 1774009599,
 'session_state': '2isLF0ClHMrDDuna54oleeye',
 'scope': 'openid email profile',
    }

@pytest.fixture(scope='session')
def kc_userinfo_response() -> dict[str, Any]:
    return {
    "name": "Test User",
    "preferred_username": "test_user",
    "given_name": "Test",
    "family_name": "User",
    "email": "test@disroot.org",
    "email_verified": True,
    "sub": "7f4296f5-ba32-434e-9c18-2ad2e40b9526"
}

@pytest.fixture
def kc_get_token_api_mock(httpx_mock: HTTPXMock, kc_get_token_response: dict[str, Any]) -> None:
    httpx_mock.add_response(
        url=f'{KEYCLOAK_BASE_API_URL}token',
        json=kc_get_token_response,
    )

@pytest.fixture
def kc_userinfo_api_mock(httpx_mock: HTTPXMock, kc_userinfo_response: dict[str, Any]) -> None:
    httpx_mock.add_response(
        url=f'{KEYCLOAK_BASE_API_URL}userinfo',
        json=kc_userinfo_response,
    )

@pytest.fixture
def kc_refresh_token_api_mock(kc_get_token_api_mock) -> None:
    pass

@pytest.fixture
def user_create_in(user_create_in_factory: UserCreateInFactory) -> UserCreateIn:
    return user_create_in_factory.build()

@pytest.fixture
def kc_get_user_return_data(user_create_in: UserCreateIn) -> dict[str, Any]:
    return {
        "id": "30e46920-b7ae-4ba8-aa6a-9e7fcf201915",
        "username": user_create_in.username,
        "firstName": user_create_in.first_name,
        "lastName": user_create_in.last_name,
        "email": user_create_in.email,
        "emailVerified": False,
        "attributes": {
            "location": [
                "ru"
            ]
        },
        "enabled": user_create_in.enabled,
        "createdTimestamp": datetime.datetime.now().timestamp(),
        "totp": False,
        "disableableCredentialTypes": [],
        "requiredActions": [],
        "notBefore": 0,
        "access": {
            "manageGroupMembership": True,
            "resetPassword": True,
            "view": True,
            "mapRoles": True,
            "impersonate": True,
            "manage": True
        }
    }

@pytest.fixture
def kc_create_new_user_api_mock(httpx_mock: HTTPXMock) -> uuid.UUID:
    kc_url = f'{settings.KEYCLOAK_SERVER_URL}admin/realms/{settings.KEYCLOAK_REALM}/users'
    random_user_uuid = uuid.uuid4()
    httpx_mock.add_response(
        status_code=HTTP_201_CREATED,
        url=kc_url,
        headers={
            'location': f'{kc_url}/{random_user_uuid}',
            'referrer-policy': 'no-referrer',
            'strict-transport-security': 'max-age=31536000; includeSubDomains',
            'x-content-type-options': 'nosniff',
            'x-frame-options': 'SAMEORIGIN',
            'x-robots-tag': 'none',
            'content-length': '0',
        }
    )
    return random_user_uuid
