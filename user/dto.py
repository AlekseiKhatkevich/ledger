from litestar.dto import DataclassDTO
from litestar.plugins.pydantic import PydanticDTO

from user.domain import UserLoginPayload, UserLoginReturn


class UserLoginPayloadDTO(PydanticDTO[UserLoginPayload]):
    pass


class UserLoginReturnDTO(DataclassDTO[UserLoginReturn]):
    pass
