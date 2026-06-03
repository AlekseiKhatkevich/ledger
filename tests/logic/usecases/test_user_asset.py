import datetime
from collections import defaultdict

from logic.db_models import AssetOperationType
from logic.usecases.user_asset import UserAssetDetailUseCase


def test_user_asset_detail_use_case_calculate_operations_summary(
        user_asset_detail_combined_out_factory,
        user_asset_operation_detail_out_factory,
):
    use_case = UserAssetDetailUseCase(datetime.timedelta(seconds=30))
    operation_purchase = user_asset_operation_detail_out_factory.batch(
        size=2,
        type=AssetOperationType.PURCHASE,
        public_key='PUBKEY1',
    )
    operation_sell = user_asset_operation_detail_out_factory.batch(
        size=2,
        type=AssetOperationType.SELL,
        public_key='PUBKEY2',
    )
    asset_data_from_db = user_asset_detail_combined_out_factory.build(
        operations=[*operation_purchase, *operation_sell]
    )

    aggregated_data = use_case._calculate_operations_summary(asset_data_from_db)

    groups = defaultdict(list)
    for obj in aggregated_data.overall:
        groups[obj.type].append(obj)

    for op_type, op_collection in zip(
            (AssetOperationType.PURCHASE, AssetOperationType.SELL),
            (operation_purchase, operation_sell),
    ):
        only_result = groups[op_type][0]
        assert only_result.key == op_type
        assert only_result.type == op_type
        assert only_result.count == len(op_collection)
        assert only_result.total_quantity == sum(op.quantity for op in op_collection)
        assert only_result.total_summ == sum(op.summ for op in op_collection)

    groups.clear()
    for obj in aggregated_data.by_public_key:
        groups[obj.key].append(obj)

    for pub_key, op_collection in zip(('PUBKEY1', 'PUBKEY2', ), (operation_purchase, operation_sell,)):
        by_pk = groups[pub_key]
        assert len(by_pk) == 1
        assert by_pk[0].key == pub_key
        assert by_pk[0].type == op_collection[0].type
        assert by_pk[0].count == 2
        assert by_pk[0].total_quantity == sum(op.quantity for op in op_collection)
        assert by_pk[0].total_summ == sum(op.summ for op in op_collection)


def test_calculate_public_key_details(
        user_asset_detail_combined_out_factory,
        user_asset_operation_detail_out_factory,
):
    use_case = UserAssetDetailUseCase(datetime.timedelta(seconds=30))
    operation_pk1 = user_asset_operation_detail_out_factory.batch(
        size=10,
        public_key='PUBKEY1',
    )
    operation_pk2 = user_asset_operation_detail_out_factory.batch(
        size=10,
        public_key='PUBKEY2',
    )
    asset_data_from_db = user_asset_detail_combined_out_factory.build(
        operations=[*operation_pk1, *operation_pk2]
    )
    aggregated_data = use_case._calculate_public_key_details(asset_data_from_db)

    assert len(aggregated_data) == 2

    groups = defaultdict(list)
    for obj in aggregated_data:
        groups[obj.public_key].append(obj)

    for key, operation_group in zip(('PUBKEY1', 'PUBKEY2', ), (operation_pk1, operation_pk2, )):
        pk_data = groups[key]
        assert pk_data[0].public_key == key
        in_stock_expected = max(
            sum(op.quantity for op in operation_group if op.type == AssetOperationType.PURCHASE) - \
               sum(op.quantity for op in operation_group if op.type == AssetOperationType.SELL),
            0,
        )
        assert pk_data[0].in_stock == in_stock_expected
        assert pk_data[0].market_value == pk_data[0].in_stock * asset_data_from_db.user_asset.price