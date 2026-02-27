from litestar import Litestar, Request, get




@get("/health")
async def health() -> dict :
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}

@get("/")
async def my_router_handler(request: Request) -> None:
    request.logger.info("inside a request1")
    return None


app = Litestar(
    [ my_router_handler, health],
    # on_startup=lifespan.on_startup,
    # on_shutdown=lifespan.on_shutdown,
    # plugins=[StructlogPlugin()],
)