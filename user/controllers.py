from keycloak import KeycloakAuthenticationError
from litestar import post, Controller, Request, Response, MediaType
from litestar.status_codes import HTTP_200_OK

from user.domain import UserLoginPayload, UserLoginReturn
from user.dto import UserLoginReturnDTO
from user.usecases.keycloaklogin import KeyCloakLoginUseCase


def keycloak_login_exception_handler(_: Request, exc: KeycloakAuthenticationError) -> Response:
    return Response(
        media_type=MediaType.JSON,
        content=exc.response_body,
        status_code=exc.response_code,
    )


class UserController(Controller):
    path = '/user'
    exception_handlers = {KeycloakAuthenticationError: keycloak_login_exception_handler}

    @post('/login', return_dto=UserLoginReturnDTO, status_code=HTTP_200_OK)
    async def login(self, data: UserLoginPayload) -> UserLoginReturn:
        return await KeyCloakLoginUseCase().execute(str(data.email), data.password.get_secret_value(),)