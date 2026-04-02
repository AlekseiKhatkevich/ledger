from faker import Faker
from polyfactory.factories import DataclassFactory

from user.domain import UserCreateIn, CreatedUserOut, User


class CustomFactory[T](DataclassFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True


class UserCreateInFactory(CustomFactory[UserCreateIn]):
    __model__ = UserCreateIn

    exist_ok = False


class CreatedUserOutFactory(CustomFactory[CreatedUserOut]):
    __model__ = CreatedUserOut


class UserFactory(CustomFactory[User]):
    __model__ = User

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()
