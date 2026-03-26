from litestar.dto import DataclassDTO, DTOConfig
from litestar.plugins.pydantic import PydanticDTO

from user.domain import UserLoginPayload, UserLoginReturn, UserCreateIn, User


class UserLoginPayloadDTO(PydanticDTO[UserLoginPayload]):
    pass

class UserLoginReturnDTO(DataclassDTO[UserLoginReturn]):
    pass

class UserCreateInDTO(DataclassDTO[UserCreateIn]):
    config = DTOConfig(
        exclude={'exist_ok', }
    )

class UserOutDTO(DataclassDTO[User]):
    pass
