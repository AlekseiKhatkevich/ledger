from litestar import Request

from user.domain import User as KC_User


async def keycloak_user(request: Request) -> KC_User:
    """Returns current KeyCloack user info"""
    return request.user
