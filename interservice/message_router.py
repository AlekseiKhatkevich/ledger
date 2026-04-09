from typing import Type, assert_never

import structlog

from interservice.domain import messages_types, MessageSubject
from interservice.handlers import PeerDiscoveryHandler, AbstractNNGHandler

log = structlog.get_logger()


class IncomingMessageRouter:

    @staticmethod
    def choose_handler(message: messages_types) -> Type[AbstractNNGHandler]:
        match message.header.subject:
            case MessageSubject.PEERDISCOVERY:
                handler = PeerDiscoveryHandler
            # case MessageSubject.SURVEY:
            #     pass
            case _ as unreachable:
                assert_never(unreachable)

        return handler
