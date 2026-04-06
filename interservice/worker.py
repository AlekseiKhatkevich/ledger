import asyncio

import pynng

from config import settings


class Node:
    def __init__(self):
        self._listener: pynng.Listener | None = None
        self.sock: pynng.Bus0 = self.init_sock()
        self.is_entrypoint = False
        self.peers = set()

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

    async def run(self):
        if not self.is_entrypoint:
            self.sock.dial(settings.NNG_BASE_ENTRYPOINT_ADR)
        await asyncio.sleep(settings.NNG_INIT_TIME_INTERVAL)
        await self.sock.asend()