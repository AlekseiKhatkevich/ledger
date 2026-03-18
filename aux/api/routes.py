from litestar import Litestar, Router, get


@get('/health', exclude_from_auth=True)
async def health() -> dict :
    """Healthcheck"""
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}

aux_router = Router(path='aux', route_handlers=(health, ), tags=('aux', ))
