import uuid
from typing import Annotated

import msgspec
from litestar.dto import DTOConfig, MsgspecDTO


class UserAssetAddressData(msgspec.Struct):
    public_key: str
    user_id: uuid.UUID
    wallet_name: list[Annotated[str, msgspec.Meta(max_length=50)]] | None = None


class UserAssetAddressDto(MsgspecDTO[UserAssetAddressData]):
    config = DTOConfig(exclude={'user_id', })
