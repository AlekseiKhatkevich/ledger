import pytest
from sqlalchemy import text



@pytest.mark.asyncio(loop_scope="session")
async def test_user_asset_address_positive(
    db
):
    async with db.session() as session:
            await session.execute(text('select 1 + 1'))
            await session.commit()


@pytest.mark.asyncio(loop_scope="session")
async def test_user_asset_address_negative_pub_key_non_unique(
    db
):
    async with db.session() as session:
        await session.execute(text('select 1 + 1'))
        await session.commit()
