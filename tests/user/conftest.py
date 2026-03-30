from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from config import settings


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

@pytest.fixture
def kc_get_token_api_mock(httpx_mock: HTTPXMock, kc_get_token_response: dict[str, Any]) -> None:
    httpx_mock.add_response(
        url=f'{settings.KEYCLOAK_SERVER_URL}realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/token',
        json=kc_get_token_response,
    )