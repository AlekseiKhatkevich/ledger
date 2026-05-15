import decimal

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from database.postgres.connection import db
from logic.db_models import UserAssetAddress, AssetTicker, UserAsset, UserAssetOperation


class CustomFactory[T](SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True
    __async_session__ = db.session
    __set_relationships__ = False
    __allow_none_optionals__ = False


class UserAssetAddressFactory(CustomFactory[UserAssetAddress]):

    @classmethod
    def public_key(cls) -> str:
        return cls.__faker__.unique.pystr(max_chars=32, min_chars=32)

    @classmethod
    def wallet_name(cls) -> list[str]:
        return cls.__faker__.pylist(nb_elements=2, variable_nb_elements=True, value_types=[str])

class AssetTickerFactory(CustomFactory[AssetTicker]):

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.pystr(max_chars=10).upper()


class UserAssetFactory(CustomFactory[UserAsset]):
    pass


class UserAssetOperationFactory(CustomFactory[UserAssetOperation]):

    @classmethod
    def quantity(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(min_value=1.0, max_value=20)

    @classmethod
    def unit_price(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(min_value=1.0, max_value=100)
