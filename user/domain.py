from dataclasses import dataclass
from typing import Literal

from pydantic import SecretStr, BaseModel


class UserLoginPayload(BaseModel):
    """For login // password /login endpoint"""
    email: str
    password: SecretStr


@dataclass
class UserLoginReturn:
    """For login // password /login endpoint, returns tokens to a user"""
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: Literal['Bearer', 'JWT']
    id_token: str
    not_before_policy: int
    session_state: str
    scope: str


@dataclass
class Keycloak401Response:
    error: str
    error_description: str
