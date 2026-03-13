from litestar import post, Controller
from litestar.status_codes import HTTP_200_OK

from user.domain import UserLoginPayload, UserLoginReturn
from user.dto import UserLoginReturnDTO
from user.usecases.keycloaklogin import KeyCloakLoginUseCase


class UserController(Controller):
    path = '/user'

    # todo респонс в сл. ошибки
    @post('/login', return_dto=UserLoginReturnDTO, status_code=HTTP_200_OK)
    async def login(self, data: UserLoginPayload) -> UserLoginReturn:
        return await KeyCloakLoginUseCase().execute(str(data.email), data.password.get_secret_value(),)