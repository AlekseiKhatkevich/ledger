from litestar import Litestar, get
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider

resource = Resource(attributes={
    SERVICE_NAME: "ledger-backend"
})
provider = TracerProvider(resource=resource)

open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)


@get("/health")
async def health() -> dict :
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}

@get("/")
async def my_router_handler() -> None:
    return None


app = Litestar(
    [ my_router_handler, health],
    plugins=[StructlogPlugin(), OpenTelemetryPlugin(open_telemetry_config)],
)