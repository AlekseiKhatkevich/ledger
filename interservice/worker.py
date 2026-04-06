
import pynng

from config import settings


class Node:
    def __init__(self):
        self._listener: pynng.Listener | None = None
        self.sock: pynng.Bus0 = self.init_sock()

    def init_sock(self) -> pynng.Bus0:
        sock = pynng.Bus0()
        try:
            self._listener = sock.listen(settings.NNG_BASE_ENTRYPOINT_ADR)
        except pynng.exceptions.AddressInUse:
            self._listener = sock.listen('abstract://')
        return sock

    @property
    def local_addr(self):
        return f'{self._listener.local_address.family_as_str}://{self.name}'

    @property
    def name(self):
        return self._listener.local_address.name

    async def run(self):
        pass