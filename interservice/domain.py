import enum
import uuid
from typing import Union

import msgspec


class MessageSubject(enum.StrEnum):
    PEERDISCOVERY = 'PEERDISCOVERY'
    KEEPALIVE = 'KEEPALIVE'


class Header(msgspec.Struct, forbid_unknown_fields=True):
    from_addr: str
    subject: MessageSubject
    id: uuid.UUID = msgspec.field(default_factory=uuid.uuid7)


class PeerDiscoveryBody(msgspec.Struct, forbid_unknown_fields=True):
    peers: set[str]


class Message[T](msgspec.Struct, tag=True, forbid_unknown_fields=True):
    header: Header
    body: T

class PeerDiscoveryMessage(Message[PeerDiscoveryBody]):
    pass
# msgspec.json.decode(e, type=Message[PeerDiscoveryBody])
# 2. Delaying decoding of part of a message
# dec = msgspec.json.Decoder(Union[PeerDiscoveryMessage, Message])
# dec.decode(e)


messages_type = Union[PeerDiscoveryMessage, Message]