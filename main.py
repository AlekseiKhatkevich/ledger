from litestar import Litestar, get
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.di import Provide
from litestar.middleware import DefineMiddleware
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import RedocRenderPlugin
from litestar.openapi.spec import Components, SecurityScheme
from litestar.plugins.problem_details import ProblemDetailsConfig, ProblemDetailsPlugin
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, CONTAINER_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api import lifespan
from api.user_asset_addresses.crud import UserAssetAddressController
from api.user_asset_operations.crud import UserAssetAddressOperationController
from api.user_assets.crud import UserAssetCrudController
from aux.api.routes import aux_router
from config import settings
from database.postgres.connection import db
from user.auth.keycloack_middleware import JWTAuthenticationMiddleware
from user.controllers import UserController
from user.dependencies import keycloak_user


def setup_opentelemetry() ->  OpenTelemetryConfig:
    resource = Resource(attributes={
        SERVICE_NAME: settings.APP_NAME,
        CONTAINER_NAME: 'ledger-backend',
    })

    provider = TracerProvider(resource=resource)

    otlp_exporter = OTLPSpanExporter()
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

    LoggingInstrumentor().instrument(set_logging_format=True)
    SQLAlchemyInstrumentor().instrument(engine=db.engine.sync_engine, enable_commenter=True)
    HTTPXClientInstrumentor().instrument()

    # Use exclude list to skip health-check traces at the middleware level.
    return OpenTelemetryConfig(exclude=['/aux/health'])


auth_mw = DefineMiddleware(
    JWTAuthenticationMiddleware,
    exclude='/docs',
)


@get("/")
async def root() -> str:
    return "ROOT"


def create_app() -> Litestar:
    open_telemetry_config_local = setup_opentelemetry()

    return Litestar(
        [
            root,
            aux_router,
            UserController,
            UserAssetCrudController,
            UserAssetAddressController,
            UserAssetAddressOperationController,
        ],
        plugins=[
            OpenTelemetryPlugin(open_telemetry_config_local),
            StructlogPlugin(),
            ProblemDetailsPlugin(ProblemDetailsConfig(enable_for_all_http_exceptions=True)),
        ],
        debug=settings.DEBUG,
        on_startup=lifespan.on_startup,
        on_shutdown=lifespan.on_shutdown,
        lifespan=lifespan.lifespan,
        middleware=[auth_mw, ],
        dependencies={'kc_user': Provide(keycloak_user)},
        openapi_config=OpenAPIConfig(
            title='Ledger',
            description='FOSS ledger 4 your crypto assets, you know...',
            version="0.0.0.0.0.0.0.1",
            render_plugins=[RedocRenderPlugin()],
            path=settings.API_SCHEMA_ENDPOINT,
            security=[{'OpenID': []}],
            components=Components(
                security_schemes={
                    "BearerToken": SecurityScheme(
                        type="http",
                        scheme="bearer",
                        bearer_format="JWT",
                    )
                },
            ),
        ),
    )


app = create_app()