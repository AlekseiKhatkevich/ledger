from litestar import Litestar, get
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider

from config import settings
from user.controllers import UserController

resource = Resource(attributes={SERVICE_NAME: "ledger-backend"})
provider = TracerProvider(resource=resource)
open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)

def set_settings(app:Litestar) -> None:
    app.state.settings = settings

@get("/health")
async def health() -> dict :
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    # todo отдельный контроллер
    return {"status":"ok"}

@get("/")
async def root() -> None:
    return "ROOT"


app = Litestar(
    [root, health, UserController],
    plugins=[OpenTelemetryPlugin(open_telemetry_config), StructlogPlugin(),],
    debug=settings.DEBUG,
    on_startup=[set_settings, ],
    openapi_config=OpenAPIConfig(
        title='Ledger',
        description='FOSS ledger 4 your crypto assets, you know...',
        version="0.0.0.0.0.0.0.1",
        render_plugins=[ScalarRenderPlugin()],
        path='/docs',
    ),
)