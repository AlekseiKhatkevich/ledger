from litestar.status_codes import HTTP_200_OK


async def test_healthcheck(test_client_no_auth) -> None:
    response = test_client_no_auth.get('/aux/health/')
    assert response.status_code == HTTP_200_OK
    assert response.json() == {'status': 'OK'}