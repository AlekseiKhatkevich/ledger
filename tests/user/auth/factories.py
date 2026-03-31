from polyfactory.factories import DataclassFactory
from user.domain import UserCreateIn



class UserCreateInFactory(DataclassFactory[UserCreateIn]):
    __model__ = UserCreateIn

    exist_ok = False