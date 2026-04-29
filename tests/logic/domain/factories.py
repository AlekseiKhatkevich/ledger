from faker import Faker
from polyfactory.factories import DataclassFactory

from api.user_assets.domain import UserAssetData


class CustomFactory[T](DataclassFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True
    __allow_none_optionals__ = False


class UserAssetDataFactory(CustomFactory[UserAssetData]):

    @classmethod
    def ticker_id(cls) -> str:
        return cls.__faker__.pystr(max_chars=10).upper()
