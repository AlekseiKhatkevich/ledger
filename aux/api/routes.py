from litestar import Router, get
from litestar.datastructures import State


@get('/health', exclude_from_auth=True)
async def health() -> dict :
    """Healthcheck"""
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}


@get('/nng_node/info', exclude_from_auth=True)
async def nng_node_info(state: State) -> dict:
    """State of nng node"""
    n = state.nng_node
    return {
        'dialers': [d for d in n.dialers.keys()],
        'local_addr': n.local_addr,
        'name': n.name,
        'event': n.stop_event.is_set(),
        'seen_messages': str(n.seen_messages) ,
    }

aux_router = Router(path='aux', route_handlers=(health, nng_node_info,), tags=('aux', ))
