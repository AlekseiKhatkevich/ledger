import subprocess
from typing import TYPE_CHECKING, AsyncGenerator, AsyncIterator

import httpx
import pytest
from _pytest.fixtures import FixtureRequest
from litestar.testing import AsyncTestClient
from sqlalchemy.util import greenlet_spawn

from database.postgres.connection import db as _db, DB
from main import app as ls_app

if TYPE_CHECKING:
    from litestar import Litestar

pytest_plugins = [
    'tests.user.fixtures',
    'tests.logic.db_models.fixtures',
    'tests.logic.domain.fixtures',
]

def pytest_addoption(parser):
    parser.addoption("--skip-alembic", action="store_true", help="Skip running alembic migrations")

@pytest.fixture
async def test_client_no_auth(app) -> AsyncIterator[AsyncTestClient[Litestar]]:
    async with AsyncTestClient(app=app) as client:
        yield client

@pytest.fixture(scope='session')
def good_jwt_token_str() -> str:
    return ('eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJkbHB5NkliMGZOR21WMExTRURDSWs0SUFsZXdsa'
            'Uc5enI1VGhWY0I5emFvIn0.eyJleHAiOjE3NzYxNjU1MzksImlhdCI6MTc3NjE2MTkzOSwianRpIjoib25ydHJvOj'
            'Q3N2VkODY3LTcyNzctZWM1Ny04MGJmLTFmNDA5MzNhMmZhNyIsImlzcyI6Imh0dHA6Ly9rZXljbG9hazo4MDgwL3J'
            'lYWxtcy90ZXN0IiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjdmNDI5NmY1LWJhMzItNDM0ZS05YzE4LTJhZDJlNDBi'
            'OTUyNiIsInR5cCI6IkJlYXJlciIsImF6cCI6ImZhc3RhcGkta2V5Y2xvYWsiLCJzaWQiOiJoUFIzN1U4aVN6UGhJR'
            'Xo1ZDdnS2RZdFQiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbIioiXSwicmVhbG1fYWNjZXNzIjp7InJvbG'
            'VzIjpbImRlZmF1bHQtcm9sZXMtdGVzdCIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJ'
            'lc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291'
            'bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiZW1haWxfd'
            'mVyaWZpZWQiOnRydWUsIm5hbWUiOiJBbGVrc2VpIEtoYXRrZXZpY2giLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJoYX'
            'JkY2FzZSIsImdpdmVuX25hbWUiOiJBbGVrc2VpIiwiZmFtaWx5X25hbWUiOiJLaGF0a2V2aWNoIiwiZW1haWwiOiJ'
            'xd2VydHkxMjM0NUBkaXNyb290Lm9yZyJ9.mtkKo5Ps18Ao0TtLjfOacYCggr4q78ki08qi6Jq5YQQWN_m-Z0E6W7y'
            'Wca8yfwPXkSSEdhWx-ExQtQioYCK7f2zaaUbGrTLPhQZ5pTq7xUukOkTgi8Xz3Gcbt8fL9NLln_4iWEBg0y0E0G0_'
            'SFHAVR7XjGpKbMftuaadUyu1R-BJEZhY8IsMnabIoY0gHw4S401HdGZ6_yTxi15YS1-htvR3VPZ_wdqIHF8bNAm40'
            '7gie1N78mc2QUlArzyzVcoTRVPy_bb-fADTNzGkkIWPIw5_37-G1NQZYTmj2nGqTaikiZ8TpqQ0eKiPGg5kecKRRP'
            'Bjd4DsgCZlcZu4avMnsg')

@pytest.fixture
async def test_client(test_client_no_auth, good_jwt_token_str) -> AsyncIterator[AsyncTestClient[Litestar]] :
        test_client_no_auth.headers = {'Authorization': f'Bearer {good_jwt_token_str}'}
        yield test_client_no_auth

@pytest.fixture
async def httpx_test_client(app, good_jwt_token_str) -> AsyncIterator[httpx.AsyncClient]:
    """
    Default Litestar async test client uses Anyio blocking portal which starts everything in a separate thread.
    This has a conflict with sa connection.begin method.
    https://github.com/litestar-org/litestar/issues/1920

    Note: it seems like Lifespan is not used in this scenario.
    """
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://testserver') as client:
        client.headers = {'Authorization': f'Bearer {good_jwt_token_str}'}
        yield client

@pytest.fixture(scope='session')
def app() -> Litestar:
    ls_app.debug = True
    return ls_app

@pytest.fixture(scope='session')
def db() -> DB:
    return _db

@pytest.fixture(autouse=True)
async def wrap_db_transactions_in_savepoint(db) -> AsyncGenerator[None]:
    async with db.make_outer_connection():
        yield

# noinspection PyInconsistentReturns
@pytest.fixture(scope='session', autouse=True)
async def apply_alembic_migrations(request: FixtureRequest) -> None:
    if request.config.getoption("--skip-alembic"):
        return None
    else:
        await greenlet_spawn(lambda: subprocess.Popen(['alembic', 'upgrade', 'head']).wait())
