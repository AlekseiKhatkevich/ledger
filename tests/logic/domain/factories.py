import decimal
from typing import Any

import msgspec
from faker import Faker
from polyfactory import PostGenerated
from polyfactory import Use
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.msgspec_factory import MsgspecFactory

from api.user_asset_addresses.domain import UserAssetAddressData, UserAssetAddressUpdateData, UserAssetAddressDeleteData
from api.user_asset_operations.domain import UserAssetOperationData, UserAssetOperationDetailOut
from api.user_assets.domain import UserAssetData, UserAssetDetailCombinedOut, UserAssetDetailOut


class CustomFactory[T: msgspec.Struct](MsgspecFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 2
    __check_model__ = True
    __allow_none_optionals__ = False



class CustomDataClassFactory[T](DataclassFactory[T]):
    __is_base_factory__ = True
    __faker__ = Faker(locale='ru_RU')
    __randomize_collection_length__ = True
    __min_collection_length__ = 1
    __max_collection_length__ = 5
    __check_model__ = True
    __allow_none_optionals__ = False


class UserAssetDataFactory(CustomFactory[UserAssetData]):

    @classmethod
    def ticker_id(cls) -> str:
        return cls.__faker__.pystr(max_chars=10).upper()


class UserAssetAddressDataFactory(CustomFactory[UserAssetAddressData]):
    pass


class UserAssetAddressUpdateDataFactory(CustomFactory[UserAssetAddressUpdateData]):
    pass

class UserAssetAddressDeleteDataFactory(CustomFactory[UserAssetAddressDeleteData]):
    pass


class UserAssetOperationDataFactory(CustomFactory[UserAssetOperationData]):

    @classmethod
    def quantity(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(min_value=0.01)

    @classmethod
    def unit_price(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(min_value=0.01)


class UserAssetDetailOutFactory(CustomDataClassFactory[UserAssetDetailOut]):

    @classmethod
    def price(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(positive=True, right_digits=4, max_value=100_000, )


def _calculate_summ(name: str, values: dict[str, Any], *args: Any, **kwargs: Any) -> decimal.Decimal:
    result = decimal.Decimal(values['quantity'] * values['unit_price'])
    return result.quantize(decimal.Decimal('0.001'), rounding=decimal.ROUND_HALF_UP)


class UserAssetOperationDetailOutFactory(CustomDataClassFactory[UserAssetOperationDetailOut]):
    summ = PostGenerated(_calculate_summ)

    @classmethod
    def id(cls) -> int:
        return cls.__faker__.pyint(min_value=1)

    @classmethod
    def quantity(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(positive=True, right_digits=4, max_value=100, )

    @classmethod
    def unit_price(cls) -> decimal.Decimal:
        return cls.__faker__.pydecimal(positive=True, right_digits=4, max_value=100_000, )


class UserAssetDetailCombinedOutFactory(CustomDataClassFactory[UserAssetDetailCombinedOut]):
    user_asset = UserAssetDetailOutFactory
    operations = Use(UserAssetOperationDetailOutFactory.batch, size=10)
    operations_summary = None
    public_key_details = None
