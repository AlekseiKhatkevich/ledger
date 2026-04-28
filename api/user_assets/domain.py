import uuid
from dataclasses import dataclass

from litestar.dto import DataclassDTO, DTOConfig


@dataclass
class UserAsset:
    name: str
    ticker_id: str
    user_id: uuid.UUID

class UserAssetDto(DataclassDTO[UserAsset]):
    config = DTOConfig(exclude={ 'user_id', })

