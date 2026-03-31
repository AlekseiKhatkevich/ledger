from polyfactory.factories import DataclassFactory
from user.domain import UserCreateIn, CreatedUserOut


class UserCreateInFactory(DataclassFactory[UserCreateIn]):
    __model__ = UserCreateIn

    exist_ok = False


class CreatedUserOutFactory(DataclassFactory[CreatedUserOut]):
    __model__ = CreatedUserOut
