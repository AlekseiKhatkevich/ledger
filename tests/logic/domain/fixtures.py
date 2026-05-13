from polyfactory.pytest_plugin import register_fixture

from tests.logic.domain.factories import (
    UserAssetDataFactory,
    UserAssetAddressDataFactory,
    UserAssetAddressUpdateDataFactory,
    UserAssetAddressDeleteDataFactory,
    UserAssetOperationDataFactory,
)

register_fixture(UserAssetDataFactory)
register_fixture(UserAssetAddressDataFactory)
register_fixture(UserAssetAddressUpdateDataFactory)
register_fixture(UserAssetAddressDeleteDataFactory)
register_fixture(UserAssetOperationDataFactory)

