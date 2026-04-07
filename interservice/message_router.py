from typing import Type

import structlog

from interservice.domain import messages_types, MessageSubject
from interservice.handlers import PeerDiscoveryHandler, AbstractNNGHandler

log = structlog.get_logger()


class IncomingMessageRouter:

    @staticmethod
    async def choose_handler(message: messages_types) -> Type[AbstractNNGHandler]:
        match message.header.subject:
            case MessageSubject.PEERDISCOVERY:
                handler = PeerDiscoveryHandler
            case _:
                raise TypeError(f'Can not find proper handler for the message {message}')

        await log.ainfo('Chosen handler for message', handler=handler, message=message)
        return handler
