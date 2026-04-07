import asyncio
import contextlib

import msgspec.msgpack
import pynng
import structlog

from aux.helpers.datastructures import FixedSizeSet
from config import settings
from interservice.domain import messages_types
from interservice.handlers import PeerDiscoveryHandler
from interservice.message_router import IncomingMessageRouter

log = structlog.get_logger()



class Node:
    def __init__(self):
        self._listener: pynng.Listener | None = None
        self.is_entrypoint = False
        self.peers = set()
        self.seen_messages = FixedSizeSet(capacity=settings.NNG_KNOWN_MESSAGES_QTY)
        self.sock: pynng.Bus0 = self.init_sock()
        self.decoder = msgspec.msgpack.Decoder(messages_types)
        self.stop_event = asyncio.Event()
        self.message_router = IncomingMessageRouter()
        self.log = log.bind(name=self.name)
        self._running_tasks = set()

    def stop(self) -> None:
        self.stop_event.set()
        self.sock.close()

    def init_sock(self) -> pynng.Bus0:
        sock = pynng.Bus0(recv_timeout=settings.NNG_RECV_TIMEOUT)
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

    async def decode_message(self, message: bytes) -> messages_types:
        decoded = self.decoder.decode(message)
        await self.log.ainfo('Decoded message', message=message)
        return decoded

    def handle_incoming_message(self, message: messages_types) -> None:
        pass

    async def run(self) -> None:
        with self.sock:
            if not self.is_entrypoint:
                self.sock.dial(settings.NNG_BASE_ENTRYPOINT_ADR)
            await asyncio.sleep(settings.NNG_INIT_TIME_INTERVAL)

            await PeerDiscoveryHandler(self).send_peers()

            await self.log.ainfo('Start working')
            while not self.stop_event.is_set():
                with contextlib.suppress(pynng.exceptions.Timeout):
                    message = await self.sock.arecv_msg()  #  here periodic timeout occurrence
                    decoded_message = await self.decode_message(message.bytes)
                    if decoded_message.header.id not in self.seen_messages:
                        handler = await self.message_router.choose_handler(decoded_message)
                        await handler(self).process_message(decoded_message)
                        self.seen_messages.add(decoded_message.header.id)
                    else:
                        await self.log.ainfo('Message was found in seen messages', message=decoded_message)

            await self.log.ainfo(f'Exiting, event is set -- {self.stop_event.is_set()}')