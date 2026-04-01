from typing import TYPE_CHECKING
from collections.abc import Iterator

import pytest

from litestar.testing import TestClient

from main import app as ls_app

if TYPE_CHECKING:
    from litestar import Litestar

ls_app.debug = True


@pytest.fixture(scope='session')
def test_client(app) -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client

@pytest.fixture(scope='session')
def app() -> Litestar:
    return ls_app