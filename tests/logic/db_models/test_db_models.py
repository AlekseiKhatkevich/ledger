import pytest
from sqlalchemy import text

from database.postgres.connection import async_session

@pytest.mark.asyncio(loop_scope="session")
async def test_user_asset_address_positive(

):
    async with async_session() as session:
            await session.execute(text('select 1 + 1'))
            await session.commit()


@pytest.mark.asyncio(loop_scope="session")
async def test_user_asset_address_negative_pub_key_non_unique(

):
    async with async_session() as session:
        await session.execute(text('select 1 + 1'))
        await session.commit()
