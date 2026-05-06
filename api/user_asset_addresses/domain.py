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


class UserAssetAddressUpdateData(msgspec.Struct):
    public_key: str
    new_data: UserAssetAddressData


class UserAssetAddressUpdateDTOIn(MsgspecDTO[UserAssetAddressUpdateData]):
    config = DTOConfig(exclude={'new_data.user_id', })


class UserAssetAddressUpdateDTOOut(MsgspecDTO[UserAssetAddressUpdateData]):
        config = DTOConfig(exclude={'new_data.user_id', 'public_key', })

