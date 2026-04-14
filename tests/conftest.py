from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest
from litestar.testing import TestClient

from main import app as ls_app

if TYPE_CHECKING:
    from litestar import Litestar

pytest_plugins = ['tests.user.fixtures']


@pytest.fixture
def test_client_no_auth(app) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client


@pytest.fixture
def test_client(test_client_no_auth) -> Iterator[TestClient[Litestar]]:
        test_client_no_auth.headers = {
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkbHB5NkliMGZOR21WMEx'
                         'TRURDSWs0SUFsZXdsaUc5enI1VGhWY0I5emFvIn0.eyJleHAiOjE3NzYxNjU1MzksImlhdCI6MTc3N'
                         'jE2MTkzOSwianRpIjoib25ydHJvOjQ3N2VkODY3LTcyNzctZWM1Ny04MGJmLTFmNDA5MzNhMmZhNyI'
                         'sImlzcyI6Imh0dHA6Ly9rZXljbG9hazo4MDgwL3JlYWxtcy90ZXN0IiwiYXVkIjoiYWNjb3VudCIsI'
                         'nN1YiI6IjdmNDI5NmY1LWJhMzItNDM0ZS05YzE4LTJhZDJlNDBiOTUyNiIsInR5cCI6IkJlYXJlciI'
                         'sImF6cCI6ImZhc3RhcGkta2V5Y2xvYWsiLCJzaWQiOiJoUFIzN1U4aVN6UGhJRXo1ZDdnS2RZdFQiL'
                         'CJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjp'
                         'bImRlZmF1bHQtcm9sZXMtdGVzdCIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iX'
                         'X0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50Iiw'
                         'ibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlb'
                         'WFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJBbGVrc2VpIEtoYXRrZXZ'
                         'pY2giLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJoYXJkY2FzZSIsImdpdmVuX25hbWUiOiJBbGVrc2VpI'
                         'iwiZmFtaWx5X25hbWUiOiJLaGF0a2V2aWNoIiwiZW1haWwiOiJxd2VydHkxMjM0NUBkaXNyb290Lm9'
                         'yZyJ9.mtkKo5Ps18Ao0TtLjfOacYCggr4q78ki08qi6Jq5YQQWN_m-Z0E6W7yWca8yfwPXkSSEdhWx'
                         '-ExQtQioYCK7f2zaaUbGrTLPhQZ5pTq7xUukOkTgi8Xz3Gcbt8fL9NLln_4iWEBg0y0E0G0_SFHAVR'
                         '7XjGpKbMftuaadUyu1R-BJEZhY8IsMnabIoY0gHw4S401HdGZ6_yTxi15YS1-htvR3VPZ_wdqIHF8b'
                         'NAm407gie1N78mc2QUlArzyzVcoTRVPy_bb-fADTNzGkkIWPIw5_37-G1NQZYTmj2nGqTaikiZ8Tpq'
                         'Q0eKiPGg5kecKRRPBjd4DsgCZlcZu4avMnsg'
    }
        yield test_client_no_auth

@pytest.fixture(scope='session')
def app() -> Litestar:
    ls_app.debug = True
    return ls_app