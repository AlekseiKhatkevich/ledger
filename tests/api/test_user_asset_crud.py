import asyncio
import pathlib
from typing import AsyncIterator
from unittest.mock import AsyncMock, patch

import httpx
import msgspec
import pytest
from httpx_sse import connect_sse, aconnect_sse
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from litestar.exceptions import LitestarException
import httpx_sse
from api.user_assets.crud import UserAssetCrudController
from api.user_assets.domain import UserAssetDetailCombinedOut
from constants import LIST_VIEW_DEFAULT_PAGE_SIZE, LIST_VIEW_MAX_PAGE_SIZE
from logic.exceptions import UserAssetNotFoundError
from litestar.testing import subprocess_async_client

ROOT = pathlib.Path(__file__).parent


async def test_user_asset_crud_create(asset_ticker_in_db, httpx_test_client, pg_user_asset_repo):
    data = {
        'name': 'test_name',
        'ticker_id': asset_ticker_in_db.name,
    }

    response = await httpx_test_client.post(
                UserAssetCrudController.path ,
                json=data,
            )

    assert response.status_code == HTTP_201_CREATED
    assert response.json() == data

    instance_from_db = await pg_user_asset_repo.get_by_field_names(
        name='test_name',
        ticker_id= asset_ticker_in_db.name,
    )
    assert instance_from_db is not None
    assert instance_from_db.user_id is not None


async def test_user_asset_crud_update(user_asset_in_db, httpx_test_client, pg_user_asset_repo):
    data = {
        'name': 'new_test_name',
        'ticker_id': user_asset_in_db.ticker_id,
    }
    response = await httpx_test_client.post(
        UserAssetCrudController.path,
        json=data,
    )

    assert response.status_code == HTTP_201_CREATED

    instance_from_db = await pg_user_asset_repo.get_by_field_names(
        name='new_test_name',
        ticker_id=user_asset_in_db.ticker_id,
    )
    assert instance_from_db is not None
    assert instance_from_db.user_id == user_asset_in_db.user_id


async def test_user_asset_crud_negative_no_ticker(httpx_test_client):
    data = {
        'name': 'test_name',
        'ticker_id': 'NE',
    }
    response = await httpx_test_client.post(
        UserAssetCrudController.path,
        json=data,
    )
    assert response.status_code == HTTP_400_BAD_REQUEST
    response_data = response.json()
    assert response_data['type'] == 'https://testserver/error-descriptions/wrong_ticker.html'
    assert response_data['title'] == 'Ticker is incorrect or unknown'
    assert response_data['detail'] == 'Provide correct ticker. All available tickers are on Coingecko.'
    assert response_data['instance'] == f'https://testserver{UserAssetCrudController.path}'


async def test_user_asset_get_all_paginated_positive(
        user_asset_operations_in_db_many,
        httpx_test_client,
):
    response = await httpx_test_client.get(
        UserAssetCrudController.path,
    )

    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert response_data['items']
    assert response_data['results_per_page'] == LIST_VIEW_DEFAULT_PAGE_SIZE
    assert not response_data['has_more']
    assert response_data['cursor']
    assert len(response_data['items']) == len(user_asset_operations_in_db_many) / 2


async def test_user_asset_get_all_paginated_positive_small_page_size(
        user_asset_operations_in_db_many,
        httpx_test_client,
):
    response = await httpx_test_client.get(
        UserAssetCrudController.path,
        params={'results_per_page': 1},
    )
    assert response.status_code == HTTP_200_OK
    response_data = response.json()
    assert len(response_data['items']) == 1
    assert response_data['cursor'] == response_data['items'][0]['ticker_id']
    assert response_data['has_more']


async def test_user_asset_get_all_paginated_positive_with_cursor(
        user_asset_operations_in_db_many,
        httpx_test_client,
        user_asset_ticker_in_db_many,
):
    first, second, third, forth, fifth = sorted(user_asset_ticker_in_db_many, key=lambda t: t.name)

    response = await httpx_test_client.get(
        UserAssetCrudController.path,
        params={'cursor': third.name},
    )

    response_data = response.json()
    assert response.status_code == HTTP_200_OK
    assert not response_data['has_more']
    assert response_data['cursor'] == fifth.name




# https://docs.litestar.dev/latest/usage/testing.html
@pytest.mark.skip('Not ready')
async def test_get_exact_user_asset_positive(
        httpx_test_client,
        user_asset_in_db,
        user_asset_operation_in_db,
        asset_ticker_price_in_db,
        good_jwt_token_str,
        app,
):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, timeout=3) as client:
        client.headers = {'Authorization': f'Bearer {good_jwt_token_str}'}
        async with aconnect_sse(
                client,
                "GET",
                f"http://backend-api:8000/user_asset/{user_asset_in_db.ticker_id}",
                headers=client.headers,
        ) as event_source:
            events = [sse async for sse in event_source.aiter_sse()]
            print(events)
