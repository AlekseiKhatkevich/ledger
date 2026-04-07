import enum
import uuid
from typing import Union, Literal

import msgspec


class MessageSubject(enum.StrEnum):
    PEERDISCOVERY = 'PEERDISCOVERY'
    SURVEY = 'SURVEY'


class Header(msgspec.Struct, forbid_unknown_fields=True):
    from_addr: str
    subject: MessageSubject
    id: uuid.UUID = msgspec.field(default_factory=uuid.uuid7)


class PeerDiscoveryBody(msgspec.Struct, forbid_unknown_fields=True):
    peers: set[str]

class SurveyBody(msgspec.Struct, forbid_unknown_fields=True):
    status: Literal['OK', 'BAD']

class Message[T](msgspec.Struct, tag=True, forbid_unknown_fields=True):
    header: Header
    body: T

class PeerDiscoveryMessage(Message[PeerDiscoveryBody]):
    pass

class SurveyMessage(Message[SurveyBody]):
    pass


messages_types = Union[
    PeerDiscoveryMessage,
    SurveyMessage,
    Message,
]