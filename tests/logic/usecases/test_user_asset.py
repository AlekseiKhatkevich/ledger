import datetime
import unittest
from collections import defaultdict
from unittest.mock import patch, AsyncMock

import msgspec
import pytest

from api.user_assets.domain import UserAssetPriceSimple
from aux.helpers.async_helpers import wrap_create_task
from aux.temporal.domain import UpdatePricesWorkflowParams
from aux.temporal.workflows import TEMPORAL_UPDATE_PRICES_FLOW
from constants import LEDGER_TASK_QUEUE
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


@pytest.mark.parametrize(
    ['asset_ticker_price_in_db', 'coingecko_called'],
    [('outdated', True), ('fresh', False)],
    indirect=['asset_ticker_price_in_db']
)
async def test_update_price_periodically(
        user_asset_detail_combined_out_factory,
        asset_ticker_price_in_db,
        user_asset_detail_out_factory,
        coingecko_called,
):
    use_case = UserAssetDetailUseCase(datetime.timedelta(seconds=0))
    asset_data_from_db = user_asset_detail_combined_out_factory.build(
        user_asset=user_asset_detail_out_factory.build(
            ticker_id=asset_ticker_price_in_db.name,
        )
    )
    with patch.object(
                UserAssetDetailUseCase,
                '_update_prices_from_coingecko',
                new=AsyncMock(return_value=[]),
            ) as mock_update_prices:
        task = await wrap_create_task(
            use_case.update_price_periodically(asset_data_from_db),
            True,
        )
        use_case.final_event.set()
        await task

        new_prices = use_case.result_queue.get_nowait()
        assert len(new_prices) == 1
        new_price = new_prices[0]
        assert new_price.name == asset_data_from_db.user_asset.ticker_id
        assert new_price.price == asset_ticker_price_in_db.price
        if coingecko_called:
            mock_update_prices.assert_awaited_once_with({asset_data_from_db.user_asset.ticker_id, })
        else:
            mock_update_prices.assert_not_awaited()


async def test_update_prices_from_coingecko(monkeypatch):
    use_case = UserAssetDetailUseCase(datetime.timedelta(seconds=0))
    ticker_names = {'BTC', }

    mock_execute_workflow, mock_client = AsyncMock(), AsyncMock()
    mock_client.execute_workflow = mock_execute_workflow
    expected_price_data = [{'name': 'BTC', 'price': '150000'}, ]
    mock_execute_workflow.return_value = expected_price_data
    monkeypatch.setattr(
        'logic.usecases.user_asset.get_client',
        AsyncMock(return_value=mock_client),
    )

    result = await use_case._update_prices_from_coingecko(ticker_names)
    updated_price_data = msgspec.convert(
            expected_price_data, type=list[UserAssetPriceSimple], from_attributes=True
        )
    assert result == updated_price_data
    mock_execute_workflow.assert_awaited_once_with(
        TEMPORAL_UPDATE_PRICES_FLOW,
        UpdatePricesWorkflowParams(tickers=ticker_names),
        id=unittest.mock.ANY,
        task_queue= LEDGER_TASK_QUEUE,
    )
    new_prices = use_case.result_queue.get_nowait()
    assert len(new_prices) == 1
    assert new_prices == updated_price_data


@pytest.mark.parametrize('asset_ticker_price_in_db', ['outdated',], indirect=True,)
async def test_check_if_price_outdated(user_asset_detail_combined_out_factory, asset_ticker_price_in_db):
    use_case = UserAssetDetailUseCase(datetime.timedelta(seconds=0))
    with patch.object(
            UserAssetDetailUseCase,
            '_update_prices_from_coingecko',
            new=AsyncMock(),
    ) as mock_update_prices_from_coingecko:
        asset_data_from_db = user_asset_detail_combined_out_factory.build()
        tickers = {asset_data_from_db.user_asset.ticker_id}

        await use_case._check_if_price_outdated(asset_data_from_db)

        mock_update_prices_from_coingecko.assert_awaited_once_with(tickers)

