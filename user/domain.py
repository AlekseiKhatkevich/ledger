from dataclasses import dataclass
from typing import Literal

from pydantic import SecretStr, BaseModel


class UserLoginPayload(BaseModel):
    email: str
    password: SecretStr


@dataclass
class UserLoginReturn:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: Literal['Bearer', 'JWT']
    id_token: str
    not_before_policy: int
    session_state: str
    scope: str
