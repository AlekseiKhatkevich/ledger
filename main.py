from litestar import Litestar, get, post
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.plugins.structlog import StructlogPlugin
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from pydantic import BaseModel, SecretStr

# from user.auth.keycloak_based import KeyCloakAuth

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


class UserLoginPayload(BaseModel):
    email: str
    password: SecretStr
#
# @post('/login')
# async def login(data: UserLoginPayload) -> dict:
#     return await KeyCloakAuth().get_token(str(data.email), str(data.password),)

app = Litestar(
    [ my_router_handler, health,],
    plugins=[StructlogPlugin(), OpenTelemetryPlugin(open_telemetry_config)],
    # debug=settings.DEBUG,
)