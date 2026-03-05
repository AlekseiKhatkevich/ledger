from litestar import Litestar, Request, get
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider

resource = Resource(attributes={
    SERVICE_NAME: "starlette-api-service"
})
provider = TracerProvider(resource=resource)

open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)


@get("/health")
async def health() -> dict :
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}

@get("/")
async def my_router_handler(request: Request) -> None:
    return None


app = Litestar(
    [ my_router_handler, health],
    # on_startup=lifespan.on_startup,
    # on_shutdown=lifespan.on_shutdown,
    plugins=[StructlogPlugin(), OpenTelemetryPlugin(open_telemetry_config)],
)