import uuid
from dataclasses import dataclass

from litestar.dto import DataclassDTO, DTOConfig


@dataclass
class UserAssetData:
    name: str
    ticker_id: str
    user_id: uuid.UUID

    def __post_init__(self) -> str:
        self.ticker_id = self.ticker_id.upper()

class UserAssetDto(DataclassDTO[UserAssetData]):
    config = DTOConfig(exclude={'user_id', })
