import logging

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
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

from api import lifespan
from api.user_asset_addresses.crud import UserAssetAddressController
from api.user_assets.crud import UserAssetCrudController
from aux.api.routes import aux_router
from config import settings
from user.auth.keycloack_middleware import JWTAuthenticationMiddleware
from user.controllers import UserController
from user.dependencies import keycloak_user

# ---------------------------------------------------------------------------
# OpenTelemetry Resource — метаданные о сервисе, прикрепляются к каждому спану.
# SERVICE_NAME позволяет в Jaeger UI сгруппировать трейсы по имени приложения.
# ---------------------------------------------------------------------------
resource = Resource(attributes={SERVICE_NAME: settings.APP_NAME})

# ---------------------------------------------------------------------------
# TracerProvider — глобальный «источник» трейсов в приложении.
# Все создаваемые спаны проходят через него и отправляются на экспорт.
# ---------------------------------------------------------------------------
provider = TracerProvider(resource=resource)

# ---------------------------------------------------------------------------
# OTLPSpanExporter — отправляет готовые спаны по gRPC на указанный endpoint.
# По умолчанию смотрит переменную окружения OTEL_EXPORTER_OTLP_ENDPOINT.
# В docker-compose мы зададим её как http://jaeger:4317.
# ---------------------------------------------------------------------------
otlp_exporter = OTLPSpanExporter()

# ---------------------------------------------------------------------------
# BatchSpanProcessor — накапливает спаны в памяти и отправляет пачками.
# Это снижает нагрузку на сеть и ускоряет работу приложения,
# т.к. экспорт не блокирует основной поток на каждый span.
# ---------------------------------------------------------------------------
processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(processor)

# ---------------------------------------------------------------------------
# Регистрируем provider глобально, чтобы trace.get_tracer(__name__)
# и автоматические инструменты Litestar использовали именно его.
# ---------------------------------------------------------------------------
trace.set_tracer_provider(provider)

# ---------------------------------------------------------------------------
# LoggingInstrumentor — перехватывает стандартный модуль logging и
# прикрепляет к каждой записи trace_id/span_id.
# Это позволяет коррелировать логи со спанами в Jaeger UI.
# ---------------------------------------------------------------------------
LoggingInstrumentor().instrument(set_logging_format=True)

# ---------------------------------------------------------------------------
# OpenTelemetryConfig для встроенного Litestar-плагина.
# Плагин автоматически создаёт спан на каждый HTTP-запрос
# и добавляет туда метаданные (метод, путь, статус и т.д.).
# ---------------------------------------------------------------------------
open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)

auth_mw = DefineMiddleware(
    JWTAuthenticationMiddleware,
    exclude='/docs',
)


# ---------------------------------------------------------------------------
# Корневой эндпойнт для быстрой проверки работоспособности.
# Внутри демонстрируем ручное создание спана и добавление событий,
# чтобы в Jaeger UI был виден не только автоматический HTTP-спан,
# но и пользовательские логи/метки.
# ---------------------------------------------------------------------------
@get("/")
async def root() -> str:
    # Получаем текущий span, который OpenTelemetryPlugin создал автоматически
    # при входе в HTTP-запрос. Если его нет — вернёт INVALID_SPAN (no-op).
    current_span = trace.get_current_span()

    # Добавляем произвольное событие (event) в спан.
    # В Jaeger оно отобразится как «log» внутри трейса.
    current_span.add_event("root_endpoint_called", {"detail": "manual event from root"})

    # Обычный Python-логгер. Благодаря LoggingInstrumentor
    # в stdout попадут trace_id и span_id — можно легко найти связанный трейс.
    logger = logging.getLogger(__name__)
    logger.info("Root endpoint was called — trace should appear in Jaeger")

    return "ROOT"


def create_app() -> Litestar:
    return Litestar(
        [
            root,
            aux_router,
            UserController,
            UserAssetCrudController,
            UserAssetAddressController,
        ],
        plugins=[
            # OpenTelemetryPlugin — встроенный плагин Litestar.
            # Он оборачивает каждый HTTP-запрос в span,
            # добавляет атрибуты (http.method, http.route, http.status_code)
            # и завершает span при отправке ответа клиенту.
            OpenTelemetryPlugin(open_telemetry_config),
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
