from litestar import Request


async def keycloak_user(request: Request):
    return request.user
