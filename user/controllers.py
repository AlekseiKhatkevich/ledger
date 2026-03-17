from keycloak import KeycloakAuthenticationError
from litestar import post, Controller, Request, Response, MediaType
from litestar.openapi.datastructures import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED

from user.domain import UserLoginPayload, UserLoginReturn, Keycloak401Response
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
    tags = ('user', )

    @post(
        '/login',
        exclude_from_auth=True,
        return_dto=UserLoginReturnDTO,
        status_code=HTTP_200_OK,
        responses={
            HTTP_401_UNAUTHORIZED: ResponseSpec(
                data_container=Keycloak401Response,
                description='Wrong credentials',
            )
        }
    )
    async def login(self, data: UserLoginPayload) -> UserLoginReturn:
        """To obtain OpenID credentials"""
        # noinspection PyTypeChecker
        return await KeyCloakLoginUseCase().execute(str(data.email), data.password.get_secret_value(),)