import asyncio
import contextlib

import msgspec.msgpack
import pynng
import structlog

from aux.helpers.datastructures import FixedSizeSet
from config import settings
from interservice.domain import messages_types
from interservice.handlers import PeerDiscoveryHandler, SurveyHandler
from interservice.message_router import IncomingMessageRouter

log = structlog.get_logger()



class Node:
    def __init__(self, survey: bool = True) -> None:
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
        self.survey = survey

    async def stop(self) -> None:
        self.stop_event.set()
        self.sock.close()
        # await asyncio.sleep(settings.NNG_RECV_TIMEOUT)

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
    def dialers(self) -> dict[str, pynng.Dialer]:
        return {dialer.url: dialer for dialer in self.sock.dialers}

    @property
    def local_addr(self) -> str:
        return f'{self._listener.local_address.family_as_str}://{self.name}'

    @property
    def name(self) -> str:
        return self._listener.local_address.name

    async def decode_message(self, message: bytes) -> messages_types:
        decoded = self.decoder.decode(message)
        await self.log.ainfo('Decoded message', message=decoded)
        return decoded

    async def handle_incoming_message(self, message: messages_types) -> None:
        handler = self.message_router.choose_handler(message)
        await handler(self).process_message(message)
        self.seen_messages.add(message.header.id)

    async def run(self) -> None:
        # if self.survey:
        #     SurveyHandler(self).start_survey_respondent()

        with self.sock:
            await asyncio.sleep(settings.NNG_INIT_TIME_INTERVAL)
            if not self.is_entrypoint:
                self.sock.dial(settings.NNG_BASE_ENTRYPOINT_ADR)
            await asyncio.sleep(settings.NNG_INIT_TIME_INTERVAL)

            await PeerDiscoveryHandler(self).send_peers()

            await self.log.ainfo('Start working')
            while not self.stop_event.is_set():
                with contextlib.suppress(pynng.exceptions.Timeout):
                    message = await self.sock.arecv_msg()  #  here periodic timeout occurrences
                    decoded_message = await self.decode_message(message.bytes)
                    if decoded_message.header.id not in self.seen_messages:
                        await self.handle_incoming_message(decoded_message)
                    else:
                        await self.log.ainfo('Message was found in seen messages', message=decoded_message)

            await self.log.ainfo(f'Exiting, event is set -- {self.stop_event.is_set()}')
