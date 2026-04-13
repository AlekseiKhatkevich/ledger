from litestar import Router, get
from litestar.datastructures import State

from aux.api.domain import NNGNodeInfo, HealthCheckStatus


@get('/health', exclude_from_auth=True)
async def health() -> HealthCheckStatus :
    """Healthcheck"""
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return HealthCheckStatus(status='OK')


@get('/nng_node/info')
async def nng_node_info(state: State) -> NNGNodeInfo:
    """State of nng node"""
    n = state.nng_node
    return NNGNodeInfo(**{
        'dialers': [d for d in n.dialers.keys()],
        'local_addr': n.local_addr,
        'name': n.name,
        'event_state': n.stop_event.is_set(),
        'seen_messages': n.seen_messages.as_set(),
        'peers': n.peers,
    })

aux_router = Router(path='aux', route_handlers=(health, nng_node_info,), tags=('aux', ))
