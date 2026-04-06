import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from interservice.worker import Node


class AbstractNNGHandler(abc.ABC):
    def __init__(self, node: Node) -> None:
        self.node = node


class PeerDiscoveryHandler(AbstractNNGHandler):

    async def send_peers(self):
        pass