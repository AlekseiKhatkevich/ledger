from litestar import Litestar, get
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider

from aux.api.routes import aux_router
from config import settings
from user.auth.keycloack_middleware import KeyCloakAuthenticationMiddleware
from user.controllers import UserController
from user.dependencies import keycloak_user

resource = Resource(attributes={SERVICE_NAME: "ledger-backend"})
provider = TracerProvider(resource=resource)
open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)

auth_mw = DefineMiddleware(
    KeyCloakAuthenticationMiddleware,
    exclude='/docs',
)

def set_settings(app:Litestar) -> None:
    app.state.settings = settings


@get("/")
async def root() -> str:
    return "ROOT"


app = Litestar(
    # [root, aux_router, UserController],
[root, aux_router],
    plugins=[OpenTelemetryPlugin(open_telemetry_config), StructlogPlugin(),],
    debug=settings.DEBUG,
    on_startup=[set_settings, ],
    middleware=[auth_mw, ],
    dependencies={'kc_user': Provide(keycloak_user)},
    openapi_config=OpenAPIConfig(
        title='Ledger',
        description='FOSS ledger 4 your crypto assets, you know...',
        version="0.0.0.0.0.0.0.1",
        render_plugins=[ScalarRenderPlugin()],
        path=settings.API_SCHEMA_ENDPOINT,
        security = [{'OpenID': []}],
        components=Components(
            security_schemes={
                "BearerToken": SecurityScheme(
                    type="http",
                    scheme="bearer",
                )
            },
        ),
    ),
)