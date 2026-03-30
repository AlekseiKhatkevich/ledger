from litestar.status_codes import HTTP_200_OK


async def test_healthcheck(test_client) -> None:
    response = test_client.get('/aux/health/')
    assert response.status_code == HTTP_200_OK
    assert response.json() == {'status': 'ok'}