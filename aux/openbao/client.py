from concurrent.futures import ThreadPoolExecutor
from functools import cache, wraps, cached_property
from typing import TYPE_CHECKING

import async_hvac
import hvac
import msgspec
from pydantic import HttpUrl, SecretStr

from aux.openbao.domain import OpenBaoSecretResponse, OpenBaoSecretResponseBatch

if TYPE_CHECKING:
    from config import OpenBaoSettingsFinal



def retry_on_auth_error(func):
    """Re-authenticate openbao client in case temporary token got outdated"""
    @wraps(func)
    async def wrapper(self: 'OpenBaoClient', *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except (async_hvac.exceptions.Forbidden, async_hvac.exceptions.Unauthorized):
            await self.authenticate()
            return await func(self, *args, **kwargs)

    return wrapper


@cache
class OpenBaoClient:
    def __init__(
            self,
            url: HttpUrl,
            unseal_keys: tuple[SecretStr, ...],
            root_token: SecretStr,
            approle_id: SecretStr,
            approle_secret_id: SecretStr,
    ) -> None:
        self.url = url
        self.unseal_keys = unseal_keys
        self.root_token = root_token
        self.approle_id = approle_id
        self.approle_secret_id = approle_secret_id
        self._client = None

    async def get_client(self) -> async_hvac.AsyncClient:
        if self._client is None:
            self._client = async_hvac.AsyncClient(url=self.url)
            await self.authenticate()
        return self._client

    async def authenticate(self) -> async_hvac.AsyncClient:
        await self._client.auth_approle(
            self.approle_id.get_secret_value(),
            self.approle_secret_id.get_secret_value(),
        )
        return self._client

    async def unseal(self) -> None:
        async with async_hvac.AsyncClient(
                url=self.url,
                token=self.root_token.get_secret_value(),
        ) as root_client:
            if await root_client.is_sealed():
                await root_client.unseal_multi(
                    [key.get_secret_value() for key in self.unseal_keys]
                )

    @retry_on_auth_error
    async def do_something(self):
        pass


class SyncOpenBaoClient:

    def __init__(self, settings: OpenBaoSettingsFinal) -> None:
        self.settings = settings

    @cached_property
    def client(self) -> hvac.Client:
        client = hvac.Client(url=self.settings.BAO_ACCESS_ADDR)
        client.auth.approle.login(
            self.settings.BAO_APPROLE_ID.get_secret_value(),
            self.settings.BAO_APPROLE_SECRET_ID.get_secret_value(),
        )
        return client

    def unseal(self) -> None:
        client = hvac.Client(
            url=self.settings.BAO_ACCESS_ADDR,
            token=self.settings.BAO_ROOT_KEY.get_secret_value(),
        )
        if client.sys.is_sealed():
            client.sys.submit_unseal_keys(
                [key.get_secret_value() for key in self.settings.BAO_UNSEAL_KEYS]
            )

    def read_secret(self, path: str, mount_point: str | None = None) -> OpenBaoSecretResponse:
        mount_point = mount_point or self.settings.BAO_KV_MOUNT_POINT
        secret = self.client.secrets.kv.read_secret_version(
            path=f'{mount_point}/{path}',
            raise_on_deleted_version=True,
        )
        return msgspec.convert(secret, OpenBaoSecretResponse)

    def read_secrets_batch(
            self,
            paths: list[str],
            max_workers: int = 5,
    ) -> OpenBaoSecretResponseBatch:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            results = list(pool.map(self.read_secret, paths))
        return OpenBaoSecretResponseBatch(responses=results)



openbao_client: OpenBaoClient


def __getattr__(name: str) -> OpenBaoClient:
    """Lazy initialization of openbao_client singleton."""
    if name == 'openbao_client':
        from config import settings
        return OpenBaoClient(
            url=settings.BAO_ACCESS_ADDR,
            unseal_keys=settings.BAO_UNSEAL_KEYS,
            root_token=settings.BAO_ROOT_KEY,
            approle_id=settings.BAO_APPROLE_ID,
            approle_secret_id=settings.BAO_APPROLE_SECRET_ID,
        )
    raise AttributeError(f'Module {__name__} has no attribute {name}')
