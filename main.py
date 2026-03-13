from dataclasses import dataclass, field
from typing import Literal, Annotated
from litestar.plugins.pydantic import PydanticDTO
from litestar import Litestar, get, post, Controller
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.dto import DataclassDTO, DTOConfig
from litestar.plugins.structlog import StructlogPlugin
from litestar.status_codes import HTTP_202_ACCEPTED, HTTP_200_OK
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from pydantic import BaseModel, SecretStr
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.dto.msgspec_dto import MsgspecDTO
import msgspec

from aux.helpers.serialization import convert_dash_to_underscore
from config import settings
from user.auth.keycloak_based import KeyCloakAuth

resource = Resource(attributes={
    SERVICE_NAME: "ledger-backend"
})
provider = TracerProvider(resource=resource)
open_telemetry_config = OpenTelemetryConfig(tracer_provider=provider)

def set_settings(app:Litestar) -> None:
    app.state.settings = settings

@get("/health")
async def health() -> dict :
    # todo добавить проверку доступности каждого внешнего сервиса (может только критичных ??)
    return {"status":"ok"}

@get("/")
async def my_router_handler() -> None:
    return "ROOT"


class UserLoginPayload(BaseModel):
    email: str
    password: SecretStr

class UserLoginPayloadDTO(PydanticDTO[UserLoginPayload]):
    pass

@dataclass
class UserLoginReturn:
    access_token: str
    expires_in: int
    refresh_expires_in: int
    refresh_token: str
    token_type: Literal['Bearer', 'JWT']
    id_token: str
    not_before_policy: int
    session_state: str
    scope: str


class UserLoginReturnDTO(DataclassDTO[UserLoginReturn]):
    pass


class UserController(Controller):
    path = '/user'

    # todo респонс в сл. ошибки
    @post('/login', return_dto=UserLoginReturnDTO, status_code=HTTP_200_OK)
    async def login(self, data: UserLoginPayload) -> UserLoginReturn:
        return_data =  await KeyCloakAuth().get_token(str(data.email), data.password.get_secret_value(),)
        return convert_dash_to_underscore(return_data, keys=('not-before-policy', ))

app = Litestar(
    [ my_router_handler, health, UserController],
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