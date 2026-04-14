from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from logic.db_models import UserAssetAddress


class CustomFactory[T](SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True


class UserAssetAddressFactory(CustomFactory[UserAssetAddress]):
    __set_relationships__ = False
    __allow_none_optionals__ = False