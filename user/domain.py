import datetime
import uuid
from dataclasses import dataclass, field
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


@dataclass
class User:
    name: str
    preferred_username: str
    given_name: str
    family_name: str
    email: str
    email_verified: bool
    sub: uuid.UUID

    @property
    def id(self) -> uuid.UUID:
        return self.sub

@dataclass
class UserCreateIn:
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    locale: Literal['ru', 'en', ] = 'ru'
    type: Literal['password', ] = 'password'
    enabled: bool = True
    exist_ok: bool = False

@dataclass
class KeyCloakToken:
    api_key: str

@dataclass
class KeyCloakRefreshToken:
    refresh_token: str

@dataclass
class Attributes:
    location: list[str]

@dataclass
class Access:
    manageGroupMembership: bool
    resetPassword: bool
    view: bool
    mapRoles: bool
    impersonate: bool
    manage: bool

@dataclass
class CreatedUserOut:
    id: uuid.UUID
    username: str
    firstName: str
    lastName: str
    email: str
    emailVerified: bool
    attributes: Attributes
    enabled: bool
    createdTimestamp: int
    totp: bool
    disableableCredentialTypes: list
    requiredActions: list
    notBefore: int
    access: Access
