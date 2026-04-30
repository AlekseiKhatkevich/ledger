import uuid
from typing import Annotated

import msgspec
from litestar.dto import DTOConfig, MsgspecDTO


class UserAssetData(msgspec.Struct):
    name: str
    ticker_id: Annotated[str, msgspec.Meta(max_length=50)]
    user_id: uuid.UUID

    def __post_init__(self) -> str:
        self.ticker_id = self.ticker_id.upper()

class UserAssetDto(MsgspecDTO[UserAssetData]):
    config = DTOConfig(exclude={'user_id', })
