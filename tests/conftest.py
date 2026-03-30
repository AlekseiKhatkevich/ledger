from typing import TYPE_CHECKING
from collections.abc import Iterator

import pytest

from litestar.testing import TestClient

from main import app

if TYPE_CHECKING:
    from litestar import Litestar

app.debug = True


@pytest.fixture(scope='function')
def test_client() -> Iterator[TestClient[Litestar]]:
    with TestClient(app=app) as client:
        yield client