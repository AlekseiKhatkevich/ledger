from keycloak import KeycloakAuthenticationError
from litestar import post, Controller, Request, Response, MediaType, get
from litestar.openapi.datastructures import ResponseSpec
from litestar.status_codes import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST

from user.auth.exceptions import DuplicateUserException
from user.domain import (UserLoginPayload,
                         UserLoginReturn,
                         Keycloak401Response,
                         User as KC_User,
                         KeyCloakRefreshToken,
                         UserCreateIn,
                         CreatedUserOut,
                         )
from user.dto import UserLoginReturnDTO, UserCreateInDTO, CreatedUserOutDTO
from user.usecases.keycloak_create_user import KeyCloakCreateUserUseCase
from user.usecases.keycloaklogin import KeyCloakLoginUseCase
from user.usecases.keycloakrefresh import KeyCloakRefreshUseCase


def keycloak_login_exception_handler(_: Request, exc: KeycloakAuthenticationError) -> Response:
    return Response(
        media_type=MediaType.JSON,
        content=exc.response_body,
        status_code=exc.response_code,
    )

def keycloak_create_user_exception_handler(_: Request, exc: DuplicateUserException) -> Response:
    return Response(
        media_type=MediaType.JSON,
        content={'detail': exc.message, 'status_code': HTTP_400_BAD_REQUEST, },
        status_code=HTTP_400_BAD_REQUEST,
    )


class UserController(Controller):
    path = '/user'
    tags = ('user',)
    exception_handlers = {
        KeycloakAuthenticationError: keycloak_login_exception_handler,
        DuplicateUserException: keycloak_create_user_exception_handler,
    }

    @post(
        '/login/via-backend',
        exclude_from_auth=True,
        return_dto=UserLoginReturnDTO,
        status_code=HTTP_200_OK,
        deprecated=True,
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

    @post(
        '/refresh/via-backend',
        exclude_from_auth=True,
        return_dto=UserLoginReturnDTO,
        status_code=HTTP_200_OK,
        deprecated=True,
    )
    async def refresh_token(self, data: KeyCloakRefreshToken) -> UserLoginReturn:
        # noinspection PyTypeChecker
        return await KeyCloakRefreshUseCase().execute(data.refresh_token)

    @get('/via-backend', deprecated=True)
    async def userinfo(self, kc_user: KC_User) -> KC_User:
        """Information about current request user"""
        return kc_user

    @post(
        '/create',
        dto=UserCreateInDTO,
        return_dto=CreatedUserOutDTO,
        exclude_from_auth=True,
        deprecated=True,
    )
    async def create_user(self, data: UserCreateIn) -> CreatedUserOut:
        # noinspection PyTypeChecker
        return await KeyCloakCreateUserUseCase().execute(data)