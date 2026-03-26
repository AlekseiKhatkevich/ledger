from litestar.dto import DataclassDTO
from litestar.plugins.pydantic import PydanticDTO

from user.domain import UserLoginPayload, UserLoginReturn, UserCreateIn, User


class UserLoginPayloadDTO(PydanticDTO[UserLoginPayload]):
    pass

class UserLoginReturnDTO(DataclassDTO[UserLoginReturn]):
    pass

class UserCreateInDTO(DataclassDTO[UserCreateIn]):
    pass

class UserOutDTO(DataclassDTO[User]):
    pass
