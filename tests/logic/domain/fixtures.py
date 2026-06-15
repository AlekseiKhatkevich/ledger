from polyfactory.pytest_plugin import register_fixture

from tests.logic.domain.factories import (
    UserAssetDataFactory,
    UserAssetAddressDataFactory,
    UserAssetAddressUpdateDataFactory,
    UserAssetAddressDeleteDataFactory,
    UserAssetOperationDataFactory,
    UserAssetDetailOutFactory,
    UserAssetOperationDetailOutFactory,
    UserAssetDetailCombinedOutFactory,
    UserAssetOperationSearchByNoteInputArgsFactory,
)

register_fixture(UserAssetDataFactory)
register_fixture(UserAssetAddressDataFactory)
register_fixture(UserAssetAddressUpdateDataFactory)
register_fixture(UserAssetAddressDeleteDataFactory)
register_fixture(UserAssetOperationDataFactory)
register_fixture(UserAssetDetailOutFactory)
register_fixture(UserAssetOperationDetailOutFactory)
register_fixture(UserAssetDetailCombinedOutFactory)
register_fixture(UserAssetOperationSearchByNoteInputArgsFactory)
