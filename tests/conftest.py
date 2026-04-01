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
def test_client(kc_userinfo_api_mock, test_client_no_auth) -> Iterator[TestClient[Litestar]]:
        test_client_no_auth.headers = {
        'Bearer': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkbHB5NkliMGZOR21WMExTR'
                  'URDSWs0SUFsZXdsaUc5enI1VGhWY0I5emFvIn0.eyJleHAiOjE3NzUwNDY3MTgsImlhdCI6MT'
                  'c3NTA0NDkxOCwianRpIjoib25ydHJvOjgxMzE3YjEwLTEyOTMtMzZkYS00NDBjLTdkNjlhMWE'
                  '5OGZkNyIsImlzcyI6Imh0dHA6Ly9rZXljbG9hazo4MDgwL3JlYWxtcy90ZXN0IiwiYXVkIjoi'
                  'YWNjb3VudCIsInN1YiI6IjdmNDI5NmY1LWJhMzItNDM0ZS05YzE4LTJhZDJlNDBiOTUyNiIsI'
                  'nR5cCI6IkJlYXJlciIsImF6cCI6ImZhc3RhcGkta2V5Y2xvYWsiLCJzaWQiOiJkTlQ1SVM3WE'
                  '1Ca0xrYWRNanBWaHpCLWgiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVh'
                  'bG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtdGVzdCIsIm9mZmxpbmVfYWNjZX'
                  'NzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7I'
                  'nJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXBy'
                  'b2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiZW1haWxfdmVyaWZpZWQ'
                  'iOnRydWUsIm5hbWUiOiJBbGVrc2VpIEtoYXRrZXZpY2giLCJwcmVmZXJyZWRfdXNlcm5hbWUiOi'
                  'JoYXJkY2FzZSIsImdpdmVuX25hbWUiOiJBbGVrc2VpIiwiZmFtaWx5X25hbWUiOiJLaGF0a2V2a'
                  'WNoIiwiZW1haWwiOiJxd2VydHkxMjM0NUBkaXNyb290Lm9yZyJ9.YiWV9w5vEJq-FFHgXUILv89'
                  'I62QujSLY3PMUsWicXlP4fGbLE9wpVkb7cgF-RzKK4PS9iphyGMk6hIcmSKLz2ysCwzwHy5pMAq8'
                  'QJtZ3ymSs4tWMf4LKCtUOJf4_IlIyOx60mYQbgqTNPkgLdwZghALjb-9b41RppTSZTp_QplOZpq'
                  '-3mh6wb-NFbiATB5-cUmkFgX_2fghs6FCcKzNzNJrCUgFImWd0UhPBjFFJ3b9I2JxSKXFFeUNS5'
                  'iWSmSNm21jAhru2ffZcJvQjACDyq2SPHXgKVb7g1Ay0LoNrj4_G4EJaQd28YJ3nxIyu53qEUvL_'
                  'xjzYvGVauwMp1tFIMw'
    }
        yield test_client_no_auth

@pytest.fixture(scope='session')
def app() -> Litestar:
    ls_app.debug = True
    return ls_app