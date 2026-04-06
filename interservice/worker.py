import asyncio

import msgspec.msgpack
import pynng

from config import settings

from collections import OrderedDict

from interservice.domain import messages_types
from interservice.handlers import PeerDiscoveryHandler


class FixedSizeSet:
    def __init__(self, capacity=100):
        self.cap = capacity
        self.d = OrderedDict()

    def add(self, x):
        if x in self.d:
            return
        elif len(self.d) >= self.cap:
            self.d.popitem(last=False)
        self.d[x] = None

    def __contains__(self, x) -> bool:
        return x in self.d

    def __repr__(self) -> str:
        return str(self.d)


class Node:
    def __init__(self):
        self._listener: pynng.Listener | None = None
        self.is_entrypoint = False
        self.peers = set()
        self.seen_messages = FixedSizeSet(capacity=settings.NNG_KNOWN_MESSAGES_QTY)
        self.sock: pynng.Bus0 = self.init_sock()
        self.decoder = msgspec.msgpack.Decoder(messages_types)

    def init_sock(self) -> pynng.Bus0:
        sock = pynng.Bus0()
        try:
            self._listener = sock.listen(settings.NNG_BASE_ENTRYPOINT_ADR)
        except pynng.exceptions.AddressInUse:
            self._listener = sock.listen('abstract://')
        else:
            self.is_entrypoint = True

        self.peers.add(self.local_addr)

        return sock

    @property
    def local_addr(self) -> str:
        return f'{self._listener.local_address.family_as_str}://{self.name}'

    @property
    def name(self) -> str:
        return self._listener.local_address.name

    def decode_message(self, message: bytes) -> messages_types:
        return self.decoder.decode(message)

    async def run(self):
        try:
            with self.sock:
                if not self.is_entrypoint:
                    self.sock.dial(settings.NNG_BASE_ENTRYPOINT_ADR)
                await asyncio.sleep(settings.NNG_INIT_TIME_INTERVAL)

                await PeerDiscoveryHandler(self).send_peers()

                while True:
                    print('Starting working')
                    msg = await self.sock.arecv_msg()
                    decoded = self.decode_message(msg.bytes)
                    print(f'{self.name}: RECEIVED "{decoded}" FROM BUS')
                    print('Message type', type(decoded))
                    self.seen_messages.add(decoded.header.id)

        finally:
                if self._listener is not None:
                    self._listener.close()
                self.sock.close()
