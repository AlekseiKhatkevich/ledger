import enum
import uuid

import msgspec


class MessageSubject(enum.StrEnum):
    PEERDISCOVERY = 'PEERDISCOVERY'


class Header(msgspec.Struct):
    from_addr: str
    subject: MessageSubject
    id: uuid.UUID


class PeerDiscoveryBody(msgspec.Struct):
    peers: set[str]


class Message[T](msgspec.Struct):
    header: Header
    body: T
# msgspec.json.decode(e, type=Message[PeerDiscoveryBody])
# 2. Delaying decoding of part of a message